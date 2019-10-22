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

    def __init__(self, logger, config, width=320, height=240, use_splitter_port=False, splitter_width=1920,
                 splitter_height=1080):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.cancelled = False

        self.logger = logger
        self.config = config

        self.width = self.config["cv_width"]
        self.height = self.config["cv_height"]
        self.use_splitter_port = use_splitter_port
        self.splitter_width = self.config["img_width"]
        self.splitter_height = self.config["img_height"]
        self.picamera_splitter_capture = None
        self.picamera_splitter_stream = None
        self.picamera_capture = None
        self.picamera_stream = None
        self.camera = None
        self.circularStream = None
        self.rotated_camera = False

        if picamera_exists:
            # Use pi camera
            self.logger.info("picamera module exists.")
            self.initialise_picamera()
        else:
            # Use webcam
            self.logger.info("picamera module not found. Using oCV VideoCapture instead.")
            self.capture = cv2.VideoCapture(0)

            self.shutter_speed = 0
            self.exposure_mode = "auto"
            self.iso = "auto"

            if use_splitter_port is True:
                self.logger.info("Using splitter port")
                self.capture.set(3, splitter_width)
                self.capture.set(4, splitter_height)
            else:
                self.capture.set(3, width)
                self.capture.set(4, height)

        self.image = None
        self.splitter_image = None

    # Main routine
    def run(self):
        while not self.is_stopped():
            try:
                if picamera_exists:
                    try:
                        # Get image from Pi camera
                        self.picamera_capture.truncate(0)
                        self.picamera_capture.seek(0)
                        s = self.picamera_stream.__next__()
                        self.image = s.array
                        self.picamera_capture.truncate(0)
                        self.picamera_capture.seek(0)

                        if self.image is None:
                            self.logger.warning("Got empty image.")
                        time.sleep(0.01)
                    except Exception as e:
                        self.logger.error("picamera update error.")
                        self.logger.exception(e)
                        self.initialise_picamera()
                        time.sleep(0.02)
                        pass

                else:
                    # Get image from webcam
                    if self.use_splitter_port:
                        ret, self.splitter_image = self.capture.read()
                        if self.splitter_image is not None:
                            self.image = imutils.resize(self.splitter_image, width=self.width, height=self.height)
                    else:
                        ret, self.image = self.capture.read()

                    if self.image is None:
                        self.logger.warning("Got empty image.")

            except KeyboardInterrupt:
                self.logger.info("Received KeyboardInterrupt. Shutting down CameraController...")
                self.stop()

    # Stop thread
    def stop(self):
        self._stop_event.set()

        if picamera_exists:
            # Close pi camera
            self.picamera_splitter_capture.truncate(0)
            self.picamera_splitter_capture.seek(0)
            self.camera.close()
            self.camera = None
            pass
        else:
            # Close webcam
            cv2.VideoCapture(0).release()

        self.logger.info('Cancelling...')

    # Check if thread is stopped
    def is_stopped(self):
        return self._stop_event.is_set()

    # Get CV image
    def get_image(self):
        if self.image is not None:
            return self.image.copy()

    # Get CV image in binary jpeg encoding format
    def get_image_binary(self):
        r, buf = cv2.imencode(".jpg", self.get_image())
        return buf

    # Get video stream
    def get_stream(self):
        if picamera_exists:
            return self.circularStream

    def start_circular_stream(self):
        if picamera_exists:
            self.camera.framerate = self.config["frame_rate"]
            self.camera.start_recording(self.circularStream, bitrate=10000000, format='h264')

    def stop_circular_stream(self):
        if picamera_exists:
            self.camera.stop_recording()

    def wait_recording(self, delay):
        if picamera_exists:
            return self.camera.wait_recording(delay)
        else:
            return None

    def clear_buffer(self):
        if picamera_exists:
            self.circularStream.clear()

    def get_thumb_image(self):
        self.logger.info("Requested thumb image.")
        if picamera_exists:
            return self.get_image_binary()
        else:
            return None

    # Get splitter image
    def get_splitter_image(self):
        self.logger.info("Requested splitter image.")
        if self.use_splitter_port:
            if picamera_exists:
                stream = io.BytesIO()
                self.camera.capture(stream, format='jpeg', use_video_port=True)
                stream.seek(0)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                # "Decode" the image from the array, preserving colour
                s = cv2.imdecode(data, 1)

                if s is not None:
                    return s.copy()
                else:
                    return None

            else:
                if self.splitter_image is not None:
                    return self.splitter_image.copy()
                else:
                    return None
        else:
            self.logger.warning("Splitter image was not opened in constructor.")
            return None

    # Initialise picamera. If already started, close and reinitialise.
    # TODO - reset with manual exposure, if it was set before.
    def initialise_picamera(self):
        if picamera_exists:
            if self.camera is not None:
                self.camera.close()

            self.camera = picamera.PiCamera()
            self.camera.framerate = self.config["frame_rate"]
            picamera.PiCamera.CAPTURE_TIMEOUT = 60
            if self.config["rotate_camera"] == 1:
                self.camera.rotation = 180
                self.rotated_camera = True
            else:
                self.camera.rotation = 0
                self.rotated_camera = False

            if self.use_splitter_port is True:
                self.camera.resolution = (self.safe_width(self.splitter_width), self.safe_height(self.splitter_height))
                self.picamera_capture = picamera.array.PiRGBArray(self.camera, size=(self.safe_width(self.width),
                                                                                     self.safe_height(self.height)))
                self.picamera_stream = self.camera.capture_continuous(self.picamera_capture, format="bgr",
                                                                      use_video_port=True, splitter_port=2,
                                                                      resize=(self.safe_width(self.width),
                                                                              self.safe_height(self.height)))
                self.circularStream = picamera.PiCameraCircularIO(self.camera,
                                                                  bitrate=10000000,
                                                                  seconds=self.config["video_duration_before_motion"] +
                                                                  self.config["video_duration_after_motion"])
                self.start_circular_stream()
                self.logger.info('Camera initialised with a resolution of %s and a framerate of %s',
                                 self.camera.resolution,
                                 self.camera.framerate)

            else:
                self.camera.resolution = (self.safe_width(self.width), self.safe_height(self.height))
                self.picamera_capture = picamera.array.PiRGBArray(self.camera)
                self.picamera_stream = self.camera.capture_continuous(self.picamera_capture, format="bgr",
                                                                      use_video_port=True)

            time.sleep(2)

    # Set camera rotation
    def set_camera_rotation(self, rotation):
        if self.rotated_camera != rotation:
            self.rotated_camera = rotation
            if self.rotated_camera is True:
                self.camera.rotation = 180
                new_config = self.config
                new_config["rotate_camera"] = 1
                module_path = os.path.abspath(os.path.dirname(__file__))
                self.config = self.update_config(new_config,
                                                 os.path.join(module_path, self.config["data_path"], 'config.json'))
            else:
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
    def safe_width(width):
        """
        Return safe width (multiple of 32)
        :param width: width in pixels
        :return: safe width in pixels
        """
        div = width % 32
        if div is 0:
            return width
        else:
            return CameraController.safe_width(width + 1)

    @staticmethod
    def safe_height(height):
        """
        Return safe height (multiple of 32)
        :param height: height in pixels
        :return: safe height in pixels
        """
        div = height % 16
        if div is 0:
            return height
        else:
            return CameraController.safe_height(height + 1)

    @staticmethod
    def update_config(new_config, config_path):
        with open(config_path, 'w') as json_file:
            contents = json.dumps(new_config, sort_keys=True, indent=4, separators=(',', ': '))
            json_file.write(contents)
        return new_config
