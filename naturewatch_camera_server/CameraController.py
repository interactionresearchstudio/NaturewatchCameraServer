import threading
import cv2
import imutils
import time
import logging
import io
import json
import numpy as np
import os
import datetime as dt
import RPi.GPIO as GPIO
import subprocess

try:
    from picamera2 import Picamera2, MappedArray
    from picamera2.encoders import H264Encoder, Quality
    from picamera2.outputs import CircularOutput
    from libcamera import controls
    from libcamera import Transform
    from bisect import bisect_left
    picamera_exists = True 
  
except ImportError:
    Picamera2 = None
    picamera_exists = False


class CameraController(threading.Thread):

    def __init__(self, logger, config):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.cancelled = False

        self.logger = logger
        self.config = config

        # Use BCM GPIO references instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)

        # Disable GPIO warnings 
        GPIO.setwarnings(False)

        # Define GPIO pins to use
        # GPIO 16 for LED 
        GPIO.setup(16, GPIO.OUT)

# Desired image resolution (lores and main images need to be kept at the same aspect ratio)
        if self.config["resolution"] == "1640x1232":
            self.resolution = "1640x1232"
            self.width = 1640
            self.height = 1232
            self.md_width = 320
            self.md_height = 240
        else:
            self.resolution = "1920x1080"
            self.width = 1920
            self.height = 1080
            self.md_width = 320
            self.md_height = 180

# Desired LED control
        if self.config["LED"] == "off":
            self.LED = "off"
        else:
            self.LED = "on"

# Set timestamp mode
        if self.config["timestamp"] == "off":
            self.timestamp = 0
        else:
            self.timestamp = 1

# Set desired sharpness
        if self.config["sharpness_mode"] == "auto":
            self.sharpness_mode = "auto"
            self.sharpness_val = 1
        else:
            self.sharpness_mode = "manual"
            self.sharpness_val = int(self.config["sharpness_val"])

# For photos
        self.picamera_photo_stream = None

# Define the font style for the timestamps
        self.colour = (255, 255, 255) # text colour
        self.bgcolour = (0, 0, 0) # background colour
        self.origin = (0, 28) # bottom left hand corner of text on hires images
        self.lores_origin = (0, 8) # bottom left hand corner of text on lores stream
        self.bgend = (390, 35) # bottom right corner of background on hi res images
        self.lores_bgend = (115, 8) # bottom right corner of background on lores stream
        self.bgstart = (0, 0) # top left corner of background on hi res images
        self.lores_bgstart = (0, 0) # top left corner of background on lores stream
        self.font = cv2.FONT_HERSHEY_SIMPLEX # hires font
        self.lores_font = cv2.FONT_HERSHEY_PLAIN #lores font
        self.scale = 1 # hires font size
        self.lores_scale = 0.6 # lores font size
        self.thickness = 2 # hires font thickness
        self.lores_thickness = 1 # lores font thickness

        self.camera = None
        self.rotated_camera = False
        self.af_enabled = False

        if picamera_exists:
            self.initialise_picamera()
            # We use a pre_callback function to add the timestamp to images and videos recorded. This doesn't apply to the live stream viewed through the web interface
            self.camera.pre_callback = self.apply_timestamp
      
        self.image = None
        self.hires_image = None

        # Set CircularOutput buffer size. One buffer per frame so it's framerate x total number of seconds we wish to retain before motion is detected. 
        # We add an extra 1.1s to ensure we get the full time expected as this was found to be necessary in testing
        self.video_buffer_size = int(self.config["frame_rate"] * (self.config["video_duration_before_motion"] + 1.1))

        self.encoder = H264Encoder(repeat=True, iperiod=15)
        self.encoder.output = CircularOutput(buffersize=self.video_buffer_size)
        self.logger.debug('CameraController: Video buffer size allocated = {}'.format(self.video_buffer_size))
        self.recording_active = False
        
    # Main routine
    def run(self):
        while not self.is_stopped():
            try:
                if picamera_exists:
                    try:
                        # Get image from Pi camera
                        self.yuvimage = self.camera.capture_array("lores")
                        if self.timestamp == 1:
                            timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
                            cv2.rectangle(self.yuvimage, self.lores_bgstart, self.lores_bgend, self.bgcolour, -1)
                            cv2.putText(self.yuvimage, timestamp, self.lores_origin, self.lores_font, fontScale=self.lores_scale, thickness=self.lores_thickness, color=self.colour)
                        self.image = cv2.cvtColor(self.yuvimage, cv2.COLOR_YUV420p2RGB)
                        if self.image is None:
                            self.logger.warning("CameraController: got empty image.")
                        # While recording we do not need to check for motion, so we only update this loop every 1s to update the web feed
                        if self.recording_active is False:
                            time.sleep(0.03)
                        else:
                            time.sleep(1)
                    except Exception as e:
                        self.logger.error("CameraController: picamera error.")
                        self.logger.exception(e)
                        self.initialise_picamera()
                        time.sleep(0.02)
            except KeyboardInterrupt:
                self.logger.i

    # Apply a datestamp to saved images and videos. This doesn't apply to the live stream viewed through the web interface
    def apply_timestamp(self, request):
        if self.timestamp == 1:
            timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
            with MappedArray(request, "main") as m:
                cv2.rectangle(m.array, self.bgstart, self.bgend, self.bgcolour, -1)
                cv2.putText(m.array, timestamp, self.origin, self.font, self.scale, self.colour, self.thickness)
  
    # Stop thread
    def stop(self):
        self._stop_event.set()

        if picamera_exists:
            # Close pi camera
            self.camera.stop_encoder()
            self.camera.stop()
            self.camera.close()
            self.camera = None

        self.logger.info('CameraController: stopping ...')

    # Check if thread is stopped
    def is_stopped(self):
        return self._stop_event.is_set()

    # Get MD image
    def get_md_image(self):
        if self.image is not None:
            return self.image.copy()

    # Get MD image in binary jpeg encoding format
    def get_image_binary(self):
        r, buf = cv2.imencode(".jpg", self.get_md_image())
        return buf

    # Start saving contents of circular video buffer to disk
    def start_saving_video(self, output_video):
        if picamera_exists:
            self.encoder.output.fileoutput = output_video
            self.encoder.output.start()

    # Stop saving contents of circular video buffer to disk
    def stop_saving_video(self):
        if picamera_exists:
            self.encoder.output.stop()
            self.encoder.output.fileoutput = None

    def start_video_stream(self):
        if picamera_exists:
            self.camera.start_encoder(self.encoder, self.encoder.output, quality=Quality.HIGH)
            self.logger.debug('CameraController: recording started to circular buffer')

    def stop_video_stream(self):
        if picamera_exists:
            self.camera.stop_encoder()
            self.logger.debug('CameraController: recording stopped')

    def wait_recording(self, delay):
        if picamera_exists:
            time.sleep(delay)

    # Get high res image
    def get_hires_image(self):
        self.logger.debug("CameraController: hires image requested.")
        if picamera_exists:
            self.hires_yuvimage = self.camera.capture_array("main")
            s = cv2.cvtColor(self.hires_yuvimage, cv2.COLOR_YUV420p2RGB)
            if s is not None:
                return s.copy()
            else:
                return None

    # Initialise picamera. If already started, close and reinitialise.
    def initialise_picamera(self):
        self.logger.debug('CameraController: initialising picamera ...')

        # If there is already a running instance, close it
        if self.camera is not None:
            self.camera.close()

        # Create a new instance of Picamera2 and attempt to connect to the camera
        try:
            self.camera = Picamera2()
        except Exception as e:
            self.logger.error('CameraController: Unable to connect to camera')
            raise Exception("Unable to connect to camera")

        # Check for module revision
        # TODO: set maximum resolution based on module revision
        self.camera_model = self.camera.camera_properties['Model']
        self.logger.info('CameraController: camera module revision {} detected.'.format(self.camera_model))

        # Set LED state based on setting in config file
        if self.LED == "off":
            #Disable LED
            GPIO.output(16, False)
            self.logger.debug('CameraController: LED disabled')
        else:
            #Enable LED
            GPIO.output(16, True)
            self.logger.debug('CameraController: LED enabled')

        # Determine FrameDuration value based on frame_rate in config file
        self.frame_duration = int(1000000 / self.config["frame_rate"])

        # Check if we need to flip the camera feed
        if self.config["rotate_camera"] == 1:
            self.rotated_camera = True
        else:
            self.rotated_camera = False

        # Set up main imaging resolution and motion detection resolution (lores) and
        self.camera.lsize = (self.md_width, self.md_height)
        self.camera.mainsize = (self.width, self.height)

        video_config = self.camera.create_video_configuration(main={"size": self.camera.mainsize, "format": "YUV420"}, lores={"size": self.camera.lsize, "format": "YUV420"}, raw={"size": self.camera.mainsize}, transform=Transform(hflip=self.rotated_camera, vflip=self.rotated_camera),controls={"FrameDurationLimits": (self.frame_duration, self.frame_duration)})
        self.camera.configure(video_config)
        self.camera.start()

        # Check the current exposure mode and apply relevant settings
        if self.config["exposure_mode"] == "auto":
            self.exposure_mode = "auto"
            self.logger.info('Initialising with automatic exposure time.')
        else:
            self.exposure_mode = "off"
            self.logger.info('Initialising with exposure time:  {}'.format(self.config["shutter_speed"]))
            self.logger.info('Initialising with analogue gain:  {}'.format(self.config["analogue_gain"]))
            self.set_exposure(self.config["shutter_speed"], self.config["analogue_gain"])

        self.logger.info('CameraController: camera initialised with a resolution of {} and a framerate of {} fps'.format(self.camera.mainsize, int(1/(self.camera.capture_metadata()["FrameDuration"]/1000000))))
        self.logger.info('CameraController: Note that frame rates above 12fps lead to dropped frames on a Pi Zero and frame rates above 25fps can lock up the Pi Zero 2W')
        self.logger.debug('CameraController: Motion detection stream prepared with resolution {}x{}.'.format(self.md_width, self.md_height))

        # Check camera model to see if autofocus is supported and enable if configured in settings file
        # imx708 models correspond to the Raspberry Pi Camera Model 3
        self.af_enable = self.config["af_enable"]
        if self.af_enable == 1:
            if "imx708" in self.camera_model:
                # Set af_enabled to True so we can just check this variable to see if we need to run an autofocus later
                self.af_enabled = True
                self.camera.set_controls({"AfMode": controls.AfModeEnum.Auto})
                self.run_autofocus()

        # Set the user configured image sharpness
        self.set_sharpness(self.sharpness_val, self.sharpness_mode)


    # Carry out the autofocus routine
    def run_autofocus(self):
        if self.af_enabled == True:
            success = self.camera.autofocus_cycle()
            i = 0
            while not success and i < 5:
                i+=1
                time.sleep(1)
            if success:
                self.logger.debug('CameraController: autofocus routine completed successfully')
            else:
                self.logger.debug('CameraController: autofocus routine timed out')


    # Set camera rotation
    def set_camera_rotation(self, rotation):
        if self.rotated_camera != rotation:
            self.rotated_camera = rotation
            if self.rotated_camera is True:
                if picamera_exists:
                    self.camera.rotation = 180
                    self.camera.stop()
                    video_config = self.camera.create_video_configuration(main={"size": self.camera.mainsize, "format": "YUV420"}, lores={"size": self.camera.lsize, "format": "YUV420"}, raw={"size": self.camera.mainsize}, transform=Transform(hflip=self.rotated_camera, vflip=self.rotated_camera))
                    self.camera.configure(video_config)
                    self.camera.start()
                new_config = self.config
                new_config["rotate_camera"] = 1
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
            else:
                if picamera_exists:
                    self.camera.rotation = 0
                    self.camera.stop()
                    video_config = self.camera.create_video_configuration(main={"size": self.camera.mainsize, "format": "YUV420"}, lores={"size": self.camera.lsize, "format": "YUV420"}, raw={"size": self.camera.mainsize}, transform=Transform(hflip=self.rotated_camera, vflip=self.rotated_camera))
                    self.camera.configure(video_config)
                    self.camera.start()
                new_config = self.config
                new_config["rotate_camera"] = 0
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))

    # Set picamera exposure
    def set_exposure(self, ExposureTime, AnalogueGain):
        if picamera_exists:
            self.camera.set_controls({"ExposureTime": ExposureTime, "AnalogueGain": AnalogueGain, "AwbMode" : controls.AwbModeEnum.Auto})
            self.exposure_mode = 'off'
            # Need to wait a short while for the new settings to take effect before we query the new value from the camera
            time.sleep(0.5)
            new_config = self.config
            new_config["shutter_speed"] = ExposureTime
            new_config["exposure_mode"] = "off"
            module_path = os.path.abspath(os.path.dirname(__file__))
            self.config = self.update_config(new_config,
                                             os.path.join(module_path, self.config["data_path"], 'config.json'))


    def get_exposure_mode(self):
        if picamera_exists:
            self.logger.debug('Exposure mode is set to: {}'.format(self.exposure_mode))
            return self.exposure_mode


    def get_MetaData(self,control):
        if picamera_exists:         
            request = self.camera.capture_request()
            metadata = request.get_metadata()
            request.release()
            self.logger.debug('{} is set to: {}'.format(control, metadata[control]))

            # Exposure values are usually set to a value close to, but not exactly equal to the value requested.
            # So when we query the actual exposure value set we need to work out which exposure from our custom list is closest to the actual value
            if control == "ExposureTime":
                ExpList = [250, 313, 400, 500, 625, 800, 1000, 1250, 1563, 2000, 2500, 3125, 4000, 5000, 6250, 8000, 10000, 12500, 16666, 20000, 25000, 33333]
                ExpValue = self.find_closest_exposure(ExpList, metadata[control])
                self.logger.debug('Closest preset exposure value is: {}'.format(ExpValue))
                return ExpValue
            else:
                return metadata[control]


    def find_closest_exposure(self, ExpList, ExpValue):
        """
        If two numbers are equally close, return the smallest number.
        """
        pos = bisect_left(ExpList, ExpValue)
        if pos == 0:
            return ExpList[0]
        if pos == len(ExpList):
            return ExpList[-1]
        before = ExpList[pos - 1]
        after = ExpList[pos]
        if after - ExpValue < ExpValue - before:
            return after
        else:
            return before


    def auto_exposure(self):
        """
        Set picamera exposure to auto
        :return: none
        """
        if picamera_exists:
            self.exposure_mode = 'auto'
            self.camera.set_controls({"ExposureTime": 0, "AnalogueGain": 0, "AwbMode" : controls.AwbModeEnum.Auto})
            new_config = self.config
            new_config["exposure_mode"] = "auto"
            module_path = os.path.abspath(os.path.dirname(__file__))
            self.config = self.update_config(new_config,
                                             os.path.join(module_path, self.config["data_path"], 'config.json'))

    # Set camera resolution
    def set_resolution(self, resolution):
        if self.resolution != resolution:
            self.resolution = resolution
            if resolution == "1640x1232":
                new_config = self.config
                new_config["resolution"] = "1640x1232"
                new_config["img_height"] = 1232
                new_config["img_width"] = 1640
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
                subprocess.run(["sudo", "systemctl", "restart", "python.naturewatch.service"])        
            else:
                new_config = self.config
                new_config["resolution"] = "1920x1080"
                new_config["img_height"] = 1080
                new_config["img_width"] = 1920
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
                subprocess.run(["sudo", "systemctl", "restart", "python.naturewatch.service"])


    # Set LED output
    def set_LED(self, LED):
        if self.LED != LED:
            self.LED = LED
            if LED == "off":
                #Disable LED
                GPIO.output(16, False)
                self.logger.debug('CameraController: LED disabled')
                new_config = self.config
                new_config["LED"] = "off"
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
            else:
                #Enable LED
                GPIO.output(16, True)
                self.logger.debug('CameraController: LED enabled')
                new_config = self.config
                new_config["LED"] = "on"
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))


    # Synchronise time with client
    def set_Time(self, clienttime):
        self.logger.info('CameraController: Synchronising time with client')
        timesync_process = subprocess.run(['/bin/date', '-s', clienttime], capture_output=True, text=True)
        if timesync_process.stderr == "":
            self.logger.info('CameraController: Time successfully synchronised with client. New time is {}'.format(clienttime))
        else:
            self.logger.warning('CameraController: Failed to synchronise time with client.')


    # Set Timestamp Mode
    def set_TimestampMode(self, timestamp):
        if timestamp == "off":
            #Timestamps disabled
            self.timestamp = 0
            self.logger.debug('CameraController: Timestamps disabled')
            new_config = self.config
            new_config["timestamp"] = "off"
            module_path = os.path.abspath(os.path.dirname(__file__))
            self.config = self.update_config(new_config,
                                             os.path.join(module_path, self.config["data_path"], 'config.json'))
        else:
            #Timestamps enabled
            self.timestamp = 1
            self.logger.debug('CameraController: Timestamps enabled')
            new_config = self.config
            new_config["timestamp"] = "on"
            module_path = os.path.abspath(os.path.dirname(__file__))
            self.config = self.update_config(new_config,
                                             os.path.join(module_path, self.config["data_path"], 'config.json'))


    # Set Camera Sharpness
    def set_sharpness(self, sharpness_val, sharpness_mode):
        self.sharpness_mode = sharpness_mode
        if self.sharpness_mode == "auto":
            sharpness_val = 1
        else:
            self.sharpness_val = int(sharpness_val)
        self.camera.set_controls({"Sharpness": sharpness_val})
        self.logger.debug('CameraController: Sharpness set to {}'.format(sharpness_val))
        new_config = self.config
        new_config["sharpness_val"] = sharpness_val
        new_config["sharpness_mode"] = sharpness_mode
        module_path = os.path.abspath(os.path.dirname(__file__))
        self.config = self.update_config(new_config,
                                         os.path.join(module_path, self.config["data_path"], 'config.json'))


    # Carry out Shutdown option
    def set_Shutdown(self, Shutdown):
        if Shutdown == "0":
            #Carry out shutdown
            subprocess.run(["sudo", "shutdown", "now"]) 
        else:
            #Carry out reboot
            subprocess.run(["sudo", "reboot", "now"]) 


    @staticmethod
    def update_config(new_config, config_path):
        with open(config_path, 'w') as json_file:
            contents = json.dumps(new_config, sort_keys=True, indent=4, separators=(',', ': '))
            json_file.write(contents)
        return new_config





