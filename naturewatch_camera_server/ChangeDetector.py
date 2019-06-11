import cv2
import numpy as np
from threading import Thread
import datetime
import time
import imutils
import logging
from naturewatch_camera_server.FileSaver import FileSaver


class ChangeDetector(Thread):

    def __init__(self, camera_controller, configuration, logger):
        super(ChangeDetector, self).__init__()

        self.config = configuration
        self.daemon = True
        self.cancelled = False

        self.camera_controller = camera_controller

        self.logger = logger

        self.file_saver = FileSaver()

        self.minWidth = self.config["min_width"]
        self.maxWidth = self.config["max_width"]
        self.minHeight = self.config["min_height"]
        self.maxHeight = self.config["max_height"]

        self.mode = "inactive"
        self.session_start_time = None
        self.avg = None
        self.lastPhotoTime = time.time()
        self.numOfPhotos = 0

        self.activeColour = (255, 255, 0)
        self.inactiveColour = (100, 100, 100)
        self.isMinActive = False
        self.currentImage = None

    def run(self):
        """
        Main run function
        :return: none
        """
        while not self.cancelled:
            try:
                self.update()
            except Exception as e:
                self.logger.exception(e)
                continue

    def cancel(self):
        """
        Cancel thread
        :return: none
        """
        self.cancelled = True
        self.camera.close()

    @staticmethod
    def save_photo(image):
        """
        Save numpy image to a jpg file
        :param image: numpy array image
        :return: none
        """
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"

        try:
            cv2.imwrite("photos/" + filename, image)
        except Exception as e:
            self.logger.error('save_photo() error: ')
            self.logger.exception(e)
            pass

    def detect_change_contours(self, img):
        """
        Detect changed contours in frame
        :param img: current image
        :return: True if it's time to capture
        """

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

        # if the contour is too small, return false
        if w > self.maxWidth or w < self.minWidth or h > self.maxHeight or h < self.minHeight:
            # return img
            return False
        else:
            if time.time() - self.lastPhotoTime >= self.config['min_photo_interval_s']:
                return True

        return False
    
    @staticmethod
    def get_largest_contour(contours):
        """
        Get the largest contour in a list of contours
        :param contours: a list of contours
        :return: the largest contour object
        """
        if not contours:
            return None
        else:
            areas = [cv2.contourArea(c) for c in contours]
            maxIndex = np.argmax(areas)
            return contours[maxIndex]

    def set_sensitivity(self, min_width, max_width):
        self.minWidth = min_width
        self.minHeight = min_width
        self.maxWidth = max_width
        self.maxHeight = max_width

    def start_photo_session(self):
        self.logger.info('Starting photo capturing')
        self.mode = "photo"
        self.session_start_time = time.time()

    def stop_session(self):
        self.logger.info('Ending photo capturing')
        self.mode = "inactive"
        self.session_start_time = time.time()

    def update(self):
        if self.mode == "photo":
            if self.detect_change_contours(self.camera_controller.get_image()):
                self.logger.info("ChangeDetector: Detected motion. Taking photo...")
                self.file_saver.save_image(self.camera_controller.get_splitter_image())

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
