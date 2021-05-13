import threading
import cv2
import imutils
import time
import logging
import io
import json
import numpy as np
import os
try:
    import picamera
    import picamera.array
    picamera_exists = True
except ImportError:
    picamera = None
    picamera_exists = False


class CameraController(threading.Thread):

    def __init__(self, logger, config):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.cancelled = False

        self.logger = logger
        self.config = config

# Desired image resolution
        self.width = self.config["img_width"]
        self.height = self.config["img_height"]

# Image resolution used for motion detection, same aspect ratio as desired image
        self.md_width = self.config["md_width"]
        self.md_height = self.md_width * self.height // self.width

# TODO: this parameter should only be required in case of photo-mode
        self.use_video_port = self.config["use_video_port"]

# For photos
        self.picamera_photo_stream = None

# For motion detection
        self.picamera_md_output = None
        self.picamera_md_stream = None

# For video
        self.picamera_video_stream = None
        self.video_bitrate = 10000000

        self.camera = None
        self.rotated_camera = False

        if picamera_exists:
            # Use pi camera
            self.logger.info("CameraController: picamera module exists.")
            self.initialise_picamera()
        else:
            # Use webcam
            self.logger.info("CameraController: picamera module not found. Using oCV VideoCapture instead.")
            self.capture = None
            self.initialise_webcam()

        self.image = None
        self.hires_image = None

    # Main routine
    def run(self):
        while not self.is_stopped():
            try:
                if picamera_exists:
                    try:
                        # Get image from Pi camera
                        self.picamera_md_output.truncate(0)
                        self.picamera_md_output.seek(0)
                        self.picamera_md_stream.__next__()
                        self.image = self.picamera_md_output.array
                        if self.image is None:
                            self.logger.warning("CameraController: got empty image.")
                        time.sleep(0.01)
                    except Exception as e:
                        self.logger.error("CameraController: picamera update error.")
                        self.logger.exception(e)
                        self.initialise_picamera()
                        time.sleep(0.02)

                else:
                    try:
                    # Get image from webcam
                        ret, self.raw_image = self.capture.read()
                        if self.raw_image is None:
                            self.logger.warning("CameraController: got empty webcam image.")
                        else:
                            self.image = imutils.resize(self.raw_image, width=self.md_width, height=self.md_height)
                        time.sleep(0.01)
                    except Exception as e:
                        self.logger.error("CameraController: webcam update error.")
                        self.logger.exception(e)
                        self.initialise_webcam()
                        time.sleep(0.02)

            except KeyboardInterrupt:
                self.logger.info("CameraController: received KeyboardInterrupt,  shutting down ...")
                self.stop()

    # Stop thread
    def stop(self):
        self._stop_event.set()

        if picamera_exists:
            # Close pi camera
            self.picamera_md_output.truncate(0)
            self.picamera_md_output.seek(0)
            self.camera.close()
            self.camera = None
        else:
            # Close webcam
            self.capture.release()

        self.logger.info('CameraController: cancelling ...')

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

    def get_video_stream(self):
        if picamera_exists:
            return self.picamera_video_stream

    def start_video_stream(self):
        if picamera_exists:
            self.picamera_video_stream.clear()
            self.camera.start_recording(self.picamera_video_stream, format='h264', bitrate=self.video_bitrate)
            self.logger.debug('CameraController: recording started')

    def stop_video_stream(self):
        if picamera_exists:
            self.camera.stop_recording()
            self.logger.debug('CameraController: recording stopped')

    def wait_recording(self, delay):
        if picamera_exists:
            return self.camera.wait_recording(delay)
        else:
            return None

    # TODO: Not used?
    def get_thumb_image(self):
        self.logger.debug("CameraController: lores image requested.")
        if picamera_exists:
            return self.get_image_binary()
        else:
            return None

    # Get high res image
    def get_hires_image(self):
        self.logger.debug("CameraController: hires image requested.")
        if picamera_exists:
            # TODO: understand the decode. Is another more intuitive way possible?
            self.picamera_photo_stream = io.BytesIO()
            self.camera.capture(self.picamera_photo_stream, format='jpeg', use_video_port=self.use_video_port)
            self.picamera_photo_stream.seek(0)
            # "Decode" the image from the stream, preserving colour
            s = cv2.imdecode(np.fromstring(self.picamera_photo_stream.getvalue(), dtype=np.uint8), 1)

            if s is not None:
                return s.copy()
            else:
                return None

        else:
            ret, raw_image = self.capture.read()
            if raw_image is None:
                self.logger.error("CameraController: webcam returned empty hires image.")
                return None
            else:
                return raw_image.copy()

    # Initialise picamera. If already started, close and reinitialise.
    # TODO - reset with manual exposure, if it was set before.
    def initialise_picamera(self):
        self.logger.debug('CameraController: initialising picamera ...')

        # If there is already a running instance, close it
        if self.camera is not None:
            self.camera.close()

        # Create a new instance
        self.camera = picamera.PiCamera()
        # Check for module revision
        # TODO: set maximum resolution based on module revision
        self.logger.debug('CameraController: camera module revision {} detected.'.format(self.camera.revision))

        # Set camera parameters
        self.camera.framerate = self.config["frame_rate"]
        self.camera.resolution = (self.width, self.height)

        picamera.PiCamera.CAPTURE_TIMEOUT = 60

        if self.config["rotate_camera"] == 1:
            self.camera.rotation = 180
            self.rotated_camera = True
        else:
            self.camera.rotation = 0
            self.rotated_camera = False

        self.logger.info('CameraController: camera initialised with a resolution of {} and a framerate of {}'.format(
            self.camera.resolution, self.camera.framerate))

# TODO: use correct port fitting the requested resolution
        # Set up low res stream for motion detection
        self.picamera_md_output = picamera.array.PiRGBArray(self.camera, size=(self.md_width, self.md_height))
        self.picamera_md_stream = self.camera.capture_continuous(self.picamera_md_output, format="bgr",
                                                                 use_video_port=True, splitter_port=2,
                                                                 resize=(self.md_width, self.md_height))
        self.logger.debug('CameraController: low res stream prepared with resolution {}x{}.'.format(self.md_width,
                                                                                                    self.md_height))

        # Set up high res stream for actual recording
        # Bitrate has to be specified so size can be calculated from the seconds specified
        # Unfortunately the effective bitrate depends on the quality-parameter specified with start_recording,
        # so the effective duration can not be predicted well
        self.picamera_video_stream = picamera.PiCameraCircularIO(self.camera,
                                                                 bitrate=self.video_bitrate,
                                                                 seconds=self.config["video_duration_before_motion"] +
                                                                 self.config["video_duration_after_motion"])
        self.logger.debug('CameraController: circular stream prepared for video.')

        time.sleep(2)

    # initialise webcam
    def initialise_webcam(self):
        if self.capture is not None:
            self.capture.release()

        self.capture = cv2.VideoCapture(0)

        self.shutter_speed = 0
        self.exposure_mode = "auto"
        self.iso = "auto"

        self.logger.info("CameraController: preparing capture...")
        self.capture.set(3, self.width)
        self.capture.set(4, self.height)

    # Set camera rotation
    def set_camera_rotation(self, rotation):
        if self.rotated_camera != rotation:
            self.rotated_camera = rotation
            if self.rotated_camera is True:
                if picamera_exists:
                    self.camera.rotation = 180
                new_config = self.config
                new_config["rotate_camera"] = 1
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
            else:
                if picamera_exists:
                    self.camera.rotation = 0
                new_config = self.config
                new_config["rotate_camera"] = 0
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))

    # Set picamera exposure
    def set_exposure(self, shutter_speed, iso):
        if picamera_exists:
            self.camera.iso = iso
            time.sleep(0.5)
            self.camera.shutter_speed = shutter_speed
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g
        else:
            self.iso = iso
            self.shutter_speed = shutter_speed
            self.exposure_mode = 'off'

    def get_exposure_mode(self):
        if picamera_exists:
            return self.camera.exposure_mode
        else:
            return self.exposure_mode

    def get_iso(self):
        if picamera_exists:
            return self.camera.iso
        else:
            return self.iso

    def get_shutter_speed(self):
        if picamera_exists:
            return self.camera.shutter_speed
        else:
            return self.shutter_speed

    def auto_exposure(self):
        """
        Set picamera exposure to auto
        :return: none
        """
        if picamera_exists:
            self.camera.iso = 0
            self.camera.shutter_speed = 0
            self.camera.exposure_mode = 'auto'
            self.camera.awb_mode = 'auto'
        else:
            self.iso = 'auto'
            self.shutter_speed = 0
            self.exposure_mode = 'auto'

    @staticmethod
    def update_config(new_config, config_path):
        with open(config_path, 'w') as json_file:
            contents = json.dumps(new_config, sort_keys=True, indent=4, separators=(',', ': '))
            json_file.write(contents)
        return new_config
