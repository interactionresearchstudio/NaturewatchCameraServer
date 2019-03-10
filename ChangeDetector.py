import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import imutils
import datetime
import time
import logging

class ChangeDetector(Thread):

    # Constructor
    def __init__(self, configuration):
        super(ChangeDetector, self).__init__()

        self.config = configuration
        self.daemon = True
        self.cancelled = False

        # initialise logging
        numeric_loglevel = getattr(logging, self.config["log_level"].upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s' % self.config["log_level"])
        logging.basicConfig(filename='/home/pi/camera.log', level=numeric_loglevel, format='%(asctime)-15s %(levelname)s: %(message)s')
        logging.info('logging initialised')

        self.camera = None
        self.hiResCapture = None
        self.hiResStream = None
        self.lowResCapture = None
        self.lowResStream = None
        self.initialise_camera()

        self.minWidth = self.config["min_width"]
        self.maxWidth = self.config["max_width"]
        self.minHeight = self.config["min_height"]
        self.maxHeight = self.config["max_height"]


        self.mode = 0
        self.avg = None
        self.lastPhotoTime = time.time()
        self.numOfPhotos = 0

        self.activeColour = (255, 255, 0)
        self.inactiveColour = (100, 100, 100)
        self.isMinActive = False
        self.currentImage = None

    # Initialise camera
    def initialise_camera(self):
        logging.info('Initialising camera ...')
        if self.camera is not None:
            self.camera.close()

        # setting resolution and framerate at construction saves time
        self.camera = PiCamera(resolution = (self.safe_width(self.config["img_width"]), self.safe_height(self.config["img_height"])),framerate = self.config["frame_rate"])
        time.sleep(1)
		
        if self.config["fix_camera_settings"] is 1:
            self.camera.iso = self.config["iso"]
            time.sleep(0.2)
            self.camera.shutter_speed = self.config["shutter_speed"]
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g

        # low resolution images for movement detection
        self.lowResCapture = PiRGBArray(self.camera, size=(self.safe_width(self.config["cv_width"]),
                                                           self.safe_height(self.config["cv_height"])))
        self.lowResStream = self.camera.capture_continuous(self.lowResCapture, format="bgr", use_video_port=True,
                                                           splitter_port=2,
                                                           resize=(self.safe_width(self.config["cv_width"]),
                                                                   self.safe_height(self.config["cv_height"])))
        # high resolution images for capturing photos
        self.hiResCapture = PiRGBArray(self.camera)
        self.hiResStream = self.camera.capture_continuous(self.hiResCapture, format="bgr", use_video_port=self.config["use_video_port"])

        logging.debug('Camera initialised with a resolution of %s and a framerate of %s', self.camera.resolution, self.camera.framerate)
        time.sleep(2)
        logging.info('Ready to capture photos')

    # Thread run
    def run(self):
        while not self.cancelled:
            try:
                self.update()
            except Exception as e:
                logging.exception(e)
                continue

    # Thread cancel
    def cancel(self):
        self.cancelled = True
        self.camera.close()

    @staticmethod
    def save_photo(image):
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"

        try:
            cv2.imwrite("photos/" + filename, image)
        except Exception as e:
            logging.error('save_photo() error: ')
            logging.exception(e)
            pass

    def detect_change_contours(self, img):
        # convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            self.avg = gray.copy().astype("float")
            return img

        # add to accumulation model and find the change
        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold, dilate and find contours
        thresh = cv2.threshold(frame_delta, self.config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        largest_contour = self.get_largest_contour(cnts)

        if largest_contour is None:
            return img

        (x, y, w, h) = cv2.boundingRect(largest_contour)

        # if the contour is too small, just return the image.
        if w > self.maxWidth or w < self.minWidth or h > self.maxHeight or h < self.minHeight:
            return img

        # otherwise, draw the rectangle
        if time.time() - self.lastPhotoTime >= self.config['min_photo_interval_s']:
            self.capture_photo()
            
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(img, "%d" % self.numOfPhotos, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return img
    
    def capture_photo(self):
        logging.info('Capturing a photo ...')
        try:
            self.hiResCapture.truncate(0)
            self.hiResCapture.seek(0)
            hrs = self.hiResStream.__next__()
        except Exception as e:
            logging.error('capture_photo() error: ')
            logging.exception(e)
            pass
        else:
            logging.debug('Captured %dx%d photo', self.hiResCapture.array.shape[1], self.hiResCapture.array.shape[0])
        if self.config["rotate_camera"] is 1:
            hi_res_image = imutils.rotate(hrs.array, angle=180)
        else:
            hi_res_image = hrs.array
        saving_thread = Thread(target=self.save_photo, args=[hi_res_image])
        saving_thread.start()
        self.numOfPhotos = self.numOfPhotos + 1
        self.lastPhotoTime = time.time()

    @staticmethod
    def get_largest_contour(contours):
        if not contours:
            return None
        else:
            areas = [cv2.contourArea(c) for c in contours]
            maxIndex = np.argmax(areas)
            return contours[maxIndex]

    def display_min_max(self, img):
        if self.isMinActive is True:
            minColour = self.activeColour
            maxColour = self.inactiveColour
        else:
            minColour = self.inactiveColour
            maxColour = self.activeColour

        cv2.rectangle(img, (int(self.config["cv_width"]/2-self.minWidth/2),
                            int(self.config["cv_height"]/2-self.minHeight/2)),
                      (int(self.config["cv_width"]/2+self.minWidth/2),
                       int(self.config["cv_height"]/2+self.minHeight/2)), minColour, 2)
        cv2.rectangle(img, (int(self.config["cv_width"]/2-self.maxWidth/2),
                            int(self.config["cv_height"]/2-self.maxHeight/2)),
                      (int(self.config["cv_width"]/2+self.maxWidth/2),
                       int(self.config["cv_height"]/2+self.maxHeight/2)), maxColour, 2)
        return img

    def increase_min_max(self, increment):
        if self.isMinActive is True:
            self.minWidth = self.minWidth + increment
            self.minHeight = self.minHeight + increment
            if self.minWidth > self.maxWidth:
                self.minWidth = self.maxWidth
                self.minHeight = self.maxHeight
        else:
            self.maxWidth = self.maxWidth + increment
            self.maxHeight = self.maxHeight + increment
            if self.maxWidth > self.config["cv_width"]:
                self.maxWidth = self.config["cv_width"]
                self.maxHeight = self.config["cv_width"]
            if self.maxHeight >= self.config["cv_height"]:
                self.maxHeight = self.config["cv_height"]

    def decrease_min_max(self, increment):
        if self.isMinActive is True:
            self.minWidth = self.minWidth - increment
            self.minHeight = self.minHeight - increment
            if self.minWidth < 0:
                self.minWidth = 0
                self.minHeight = 0
        else:
            self.maxWidth = self.maxWidth - increment
            self.maxHeight = self.maxHeight - increment
            if self.maxWidth < self.minWidth:
                self.maxWidth = self.minWidth
                self.maxHeight = self.minHeight
            if self.maxWidth < self.config["cv_height"]:
                self.maxHeight = self.maxWidth
            elif self.maxWidth >= self.config["cv_height"]:
                self.maxHeight = self.config["cv_height"]

    def arm(self):
        logging.info('Starting photo capturing')
        self.mode = 1

    def disarm(self):
        logging.info('Ending photo capturing')
        self.mode = 0

    def rotate_camera(self):
        self.config["rotate_camera"] = 1 - self.config["rotate_camera"]
        return self.config

    def auto_exposure(self):
        self.camera.iso = 0
        self.camera.shutter_speed = 0
        self.camera.exposure_mode = 'auto'
        self.camera.awb_mode = 'auto'

        self.config["fix_camera_settings"] = 0
        return self.config

    def fix_exposure(self, shutter_speed):
        self.camera.iso = 800
        time.sleep(0.5)
        self.camera.shutter_speed = shutter_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g

        self.config["shutter_speed"] = shutter_speed
        self.config["fix_camera_settings"] = 1

        return self.config

    def update(self):
        try:
            self.lowResCapture.truncate(0)
            self.lowResCapture.seek(0)

            lrs = self.lowResStream.__next__()

            if self.config["rotate_camera"] is 1:
                self.currentImage = imutils.rotate(lrs.array, angle=180)
            else:
                self.currentImage = lrs.array

            if self.mode == 0:
                self.currentImage = self.display_min_max(self.currentImage)
            elif self.mode == 1:
                self.currentImage = self.detect_change_contours(self.currentImage)

        except Exception as e:
            logging.warning('update error')
            logging.exception(e)
            self.initialise_camera()
            pass

    def get_current_image(self):
        return self.currentImage.copy()

    @staticmethod
    def safe_width(width):
        div = width % 32
        if div is 0:
            return width
        else:
            return ChangeDetector.safe_width(width-1)

    @staticmethod
    def safe_height(height):
        div = height % 16
        if div is 0:
            return height
        else:
            return ChangeDetector.safe_height(height-1)

