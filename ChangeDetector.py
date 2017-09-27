import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import datetime
import time
import json
import os

os.chdir("/home/pi/CameraServer")
config = json.load(open("config.json"))
os.chdir("/var/www/html/photos")


class ChangeDetector(Thread):

    def __init__(self):
        super(ChangeDetector, self).__init__()
        self.daemon = True
        self.cancelled = False

        self.config = json.load(open("config.json"))

        self.camera = PiCamera()
        self.camera.resolution = (1024, 768)
        self.framerate = 30
        self.hiResCapture = PiRGBArray(self.camera)
        self.lowResCapture = PiRGBArray(self.camera, size=(320, 240))
        self.hiResStream = self.camera.capture_continuous(self.hiResCapture, format="bgr", use_video_port=True)
        self.lowResStream = self.camera.capture_continuous(self.lowResCapture, format="bgr", use_video_port=True, splitter_port=2, resize=(320,240))

        self.minWidth = config["min_width"]
        self.maxWidth = config["max_width"]
        self.minHeight = config["min_height"]
        self.maxHeight = config["max_height"]

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

    def takePhoto(self, image):
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"
        cv2.imwrite(filename, image)

    def rotateImage(self, img):
        (h,w) = img.shape[:2]
        center = (w/2, h/2)
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        return cv2.warpAffine(img, M, (w,h))

    def detectChangeContours(self, img):
        # convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if self.avg is None:
            self.avg = gray.copy().astype("float")
            return img

        # add to accumulation model and find the change
        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold, dilate and find contours
        thresh = cv2.threshold(frameDelta, config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        largestContour = self.getLargestContour(cnts)

        if largestContour is None:
            return img

        (x, y, w, h) = cv2.boundingRect(largestContour)

        # if the contour is too small, just return the image.
        if w > self.maxWidth or w < self.minWidth or h > self.maxHeight or h < self.minHeight:
            return img

        # otherwise, draw the rectangle
        if time.time() - self.lastPhotoTime > config['min_photo_interval_s']:
            hrs = self.hiResStream.next()
            hiresImage = hrs.array
            self.hiResCapture.truncate(0)
            self.hiResCapture.seek(0)
            self.takePhoto(hiresImage)
            self.numOfPhotos = self.numOfPhotos + 1
            self.lastPhotoTime = time.time()

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(img, "%d" % self.numOfPhotos, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

        return img

    def getLargestContour(self, contours):
        if not contours:
            return None
        else:
            areas = [cv2.contourArea(c) for c in contours]
            maxIndex = np.argmax(areas)
            return contours[maxIndex]

    def displayMinMax(self, img):
        if self.isMinActive is True:
            minColour = self.activeColour
            maxColour = self.inactiveColour
        else:
            minColour = self.inactiveColour
            maxColour = self.activeColour

        cv2.rectangle(img, (320/2-self.minWidth/2,240/2-self.minHeight/2), (320/2+self.minWidth/2,240/2+self.minHeight/2), minColour, 2)
        cv2.rectangle(img, (320/2-self.maxWidth/2,240/2-self.maxHeight/2), (320/2+self.maxWidth/2,240/2+self.maxHeight/2), maxColour, 2)
        return img

    def increaseMinMax(self, increment):
        if self.isMinActive is True:
            self.minWidth = self.minWidth + increment
            self.minHeight = self.minHeight + increment
            if self.minWidth > self.maxWidth:
                self.minWidth = self.maxWidth
                self.minHeight = self.maxHeight
        else:
            self.maxWidth = self.maxWidth + increment
            self.maxHeight = self.maxHeight + increment
            if self.maxWidth > 320:
                self.maxWidth = 320
                self.maxHeight = 320
            if self.maxHeight >= 240:
                self.maxHeight = 240

    def decreaseMinMax(self, increment):
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
            if self.maxWidth < 240:
                self.maxHeight = self.maxWidth
            elif self.maxWidth >= 240:
                self.maxHeight = 240

    def arm(self):
        self.mode = 1

    def disarm(self):
        self.mode = 0

    def update(self):
        lrs = self.lowResStream.next()
        self.currentImage = lrs.array
        self.lowResCapture.truncate(0)
        self.lowResCapture.seek(0)

        if self.mode == 0:
            self.currentImage = self.displayMinMax(self.currentImage)
        elif self.mode == 1:
            self.currentImage = self.detectChangeContours(self.currentImage)

    def getCurrentImage(self):
        return self.currentImage
