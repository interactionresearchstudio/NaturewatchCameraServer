import threading
import cv2
import imutils
import time
import logging
try:
    import picamera
    import picamera.array
    picamera_exists = True
except ImportError:
    picamera = None
    picamera_exists = False


class CameraController(threading.Thread):

    def __init__(self, width=320, height=240, use_splitter_port=False, splitter_width=1920, splitter_height=1080):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.cancelled = False

        self.width = width
        self.height = height
        self.use_splitter_port = use_splitter_port
        self.splitter_width = splitter_width
        self.splitter_height = splitter_height
        self.picamera_splitter_capture = None
        self.picamera_splitter_stream = None
        self.picamera_capture = None
        self.picamera_stream = None
        self.camera = None
        self.rotated_camera = False

        # Truncate and open log file
        with open('camera_controller.log', 'w'):
            pass
        logging.basicConfig(filename='camera_controller.log', level=logging.DEBUG)

        if picamera_exists:
            # Use pi camera
            logging.info("picamera module exists.")
            self.initialise_picamera()

        else:
            # Use webcam
            logging.info("picamera module not found. Using oCV VideoCapture instead.")
            self.capture = cv2.VideoCapture(0)

            if use_splitter_port is True:
                logging.info("Using splitter port")
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

                        if self.image is None:
                            logging.warning("Got empty image.")

                    except Exception as e:
                        logging.error("picamera update error.")
                        logging.exception(e)
                        self.initialise_picamera()
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
                        logging.warning("Got empty image.")
            except KeyboardInterrupt:
                logging.info("Received KeyboardInterrupt. Shutting down CameraController...")
                self.stop()

    # Stop thread
    def stop(self):
        self._stop_event.set()

        if picamera_exists:
            # Close pi camera
            self.camera.close()
            pass
        else:
            # Close webcam
            cv2.VideoCapture(0).release()

        logging.info('Cancelling...')

    # Check if thread is stopped
    def is_stopped(self):
        return self._stop_event.is_set()

    # Get CV image
    def get_image(self):
        if self.image is not None:
            if self.rotated_camera is True:
                return imutils.rotate(self.image.copy(), angle=180)
            else:
                return self.image.copy()

    # Get CV image in binary jpeg encoding format
    def get_image_binary(self):
        r, buf = cv2.imencode(".jpg", self.get_image())
        return buf

    # Get splitter image
    def get_splitter_image(self):
        logging.info("Requested splitter image.")
        if self.use_splitter_port:
            if picamera_exists:
                self.picamera_splitter_capture.truncate(0)
                self.picamera_splitter_capture.seek(0)
                s = self.picamera_splitter_stream.__next__()
                if s.array is not None:
                    if self.rotated_camera is True:
                        return imutils.rotate(s.array.copy(), angle=180)
                    else:
                        return s.array.copy()
                else:
                    return None

            else:
                if self.splitter_image is not None:
                    return self.splitter_image.copy()
                else:
                    return None
        else:
            logging.warning("Splitter image was not opened in constructor.")
            return None

    # Initialise picamera. If already started, close and reinitialise.
    # TODO - reset with manual exposure, if it was set before.
    def initialise_picamera(self):
        if picamera_exists:
            if self.camera is not None:
                self.camera.close()

            self.camera = picamera.PiCamera()
            self.camera.framerate = 30
            picamera.PiCamera.CAPTURE_TIMEOUT = 60

            if self.use_splitter_port is True:
                self.camera.resolution = (self.safe_width(self.splitter_width), self.safe_height(self.splitter_height))
                self.picamera_splitter_capture = picamera.array.PiRGBArray(self.camera)
                self.picamera_capture = picamera.array.PiRGBArray(self.camera, size=(self.safe_width(self.width),
                                                                                     self.safe_height(self.height)))
                self.picamera_splitter_stream = self.camera.capture_continuous(self.picamera_splitter_capture,
                                                                               format="bgr", use_video_port=True)
                self.picamera_stream = self.camera.capture_continuous(self.picamera_capture, format="bgr",
                                                                      use_video_port=True, splitter_port=2,
                                                                      resize=(self.safe_width(self.width),
                                                                              self.safe_height(self.height)))
            else:
                self.camera.resolution = (self.safe_width(self.width), self.safe_height(self.height))
                self.picamera_capture = picamera.array.PiRGBArray(self.camera)
                self.picamera_stream = self.camera.capture_continuous(self.picamera_capture, format="bgr",
                                                                      use_video_port=True)

            time.sleep(2)

    # Set camera rotation
    def set_camera_rotation(self, rotation):
        self.rotated_camera = rotation

    # Set picamera exposure
    def set_exposure(self, shutter_speed):
        if picamera_exists:
            self.camera.iso = 800
            time.sleep(0.5)
            self.camera.shutter_speed = shutter_speed
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g

    # Set picamera exposure to auto
    def auto_exposure(self):
        if picamera_exists:
            self.camera.iso = 0
            self.camera.shutter_speed = 0
            self.camera.exposure_mode = 'auto'
            self.camera.awb_mode = 'auto'

    # Return safe width (multiple of 32)
    @staticmethod
    def safe_width(width):
        div = width % 32
        if div is 0:
            return width
        else:
            return CameraController.safe_width(width + 1)

    # Return safe height (multiple of 32)
    @staticmethod
    def safe_height(height):
        div = height % 16
        if div is 0:
            return height
        else:
            return CameraController.safe_height(height + 1)

# Instatiate one camera controller for all server routes
camera_controller = CameraController(use_splitter_port=True)