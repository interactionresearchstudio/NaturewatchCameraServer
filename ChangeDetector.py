import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import imutils
import datetime
import time


class ChangeDetector(Thread):

    def __init__(self, configuration):
        super(ChangeDetector, self).__init__()
        self.daemon = True
        self.cancelled = False

        self.config = configuration

        self.camera = PiCamera()
        self.camera.resolution = (self.config["img_width"], self.config["img_height"])
        self.framerate = 30
        self.hiResCapture = PiRGBArray(self.camera)
        self.lowResCapture = PiRGBArray(self.camera, size=(self.config["cv_width"], self.config["cv_height"]))
        self.hiResStream = self.camera.capture_continuous(self.hiResCapture, format="bgr", use_video_port=True)
        self.lowResStream = self.camera.capture_continuous(self.lowResCapture, format="bgr", use_video_port=True,
                                                           splitter_port=2, resize=(self.config["cv_width"],
                                                                                    self.config["cv_height"]))

        self.minWidth = self.config["min_width"]
        self.maxWidth = self.config["max_width"]
        self.minHeight = self.config["min_height"]
        self.maxHeight = self.config["max_height"]

        self.mode = 0
        self.avg = None
        self.lastPhotoTime = 0
        self.numOfPhotos = 0

        self.activeColour = (255, 255, 0)
        self.inactiveColour = (100, 100, 100)
        self.isMinActive = False
        self.currentImage = None

        time.sleep(0.5)

    def run(self):
        while not self.cancelled:
            self.update()

    def cancel(self):
        self.cancelled = True
        self.camera.close()

    @staticmethod
    def take_photo(image):
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"
        cv2.imwrite(filename, image)

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
        if time.time() - self.lastPhotoTime > self.config['min_photo_interval_s']:
            hrs = self.hiResStream.next()
            if self.config["rotate_camera"] is 1:
                hi_res_image = imutils.rotate(hrs.array, angle=180)
            else:
                hi_res_image = hrs.array
            self.hiResCapture.truncate(0)
            self.hiResCapture.seek(0)
            self.take_photo(hi_res_image)
            self.numOfPhotos = self.numOfPhotos + 1
            self.lastPhotoTime = time.time()

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(img, "%d" % self.numOfPhotos, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return img

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

        cv2.rectangle(img, (self.config["cv_width"]/2-self.minWidth/2, self.config["cv_height"]/2-self.minHeight/2),
                      (self.config["cv_width"]/2+self.minWidth/2, self.config["cv_height"]/2+self.minHeight/2),
                      minColour, 2)
        cv2.rectangle(img, (self.config["cv_width"]/2-self.maxWidth/2, self.config["cv_height"]/2-self.maxHeight/2),
                      (self.config["cv_width"]/2+self.maxWidth/2, self.config["cv_height"]/2+self.maxHeight/2),
                      maxColour, 2)
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
        self.mode = 1

    def disarm(self):
        self.mode = 0

    def update(self):
        lrs = self.lowResStream.next()
        if self.config["rotate_camera"] is 1:
            self.currentImage = imutils.rotate(lrs.array, angle=180)
        else:
            self.currentImage = lrs.array
        self.lowResCapture.truncate(0)
        self.lowResCapture.seek(0)

        if self.mode == 0:
            self.currentImage = self.display_min_max(self.currentImage)
        elif self.mode == 1:
            self.currentImage = self.detect_change_contours(self.currentImage)

    def get_current_image(self):
        return self.currentImage
