import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import threading
import imutils
import datetime
import time
import logging
import os

class ChangeDetector(Thread):
    lock = threading.Lock()

    # Constructor
    def __init__(self, configuration):
        super(ChangeDetector, self).__init__()

        logging.basicConfig(filename='/home/pi/detector_error.log', level=logging.DEBUG)

        self.daemon = True
        self.cancelled = False

        self.config = configuration

        self.camera = PiCamera()
        self.camera.resolution = (self.safe_width(self.config["img_width"]), self.safe_height(self.config["img_height"]))
        self.framerate = 24

        if self.config["fix_camera_settings"] is 1:
            self.camera.iso = self.config["iso"]
            time.sleep(0.2)
            self.camera.shutter_speed = self.config["shutter_speed"]
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g

        self.hiResCapture = PiRGBArray(self.camera)
        self.lowResCapture = PiRGBArray(self.camera, size=(self.safe_width(self.config["cv_width"]), self.safe_height(self.config["cv_height"])))
        self.hiResStream = self.camera.capture_continuous(self.hiResCapture, format="bgr", use_video_port=True)
        self.lowResStream = self.camera.capture_continuous(self.lowResCapture, format="bgr", use_video_port=True,
                                                           splitter_port=2, resize=(self.safe_width(self.config["cv_width"]),
                                                                                    self.safe_height(self.config["cv_height"])))

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

        self.error = False
        self.delta = time.time()
        time.sleep(0.5)

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
        logging.debug('cancelled')
        self.cancelled = True
        self.camera.close()

    @staticmethod
    def save_photo(image):
        ChangeDetector.lock.acquire()
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"

        try:
            logging.info('writing: ' + filename)
            cv2.imwrite("photos/" + filename, image)
        except Exception as e:
            logging.debug('take_photo() error: ')
            logging.exception(e)
            pass
        finally:
            ChangeDetector.lock.release()

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
        logging.info('Taking a photo...')
        self.hiResCapture.truncate(0)
        self.hiResCapture.seek(0)
        hrs = self.hiResStream.__next__()
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
        self.mode = 1

    def disarm(self):
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
                if self.error:
                    logging.debug('update setting image')
                self.currentImage = lrs.array

            if self.error:
                logging.debug('update truncating again')
            self.lowResCapture.truncate(0)
            self.lowResCapture.seek(0)

            if self.mode == 0:
                self.currentImage = self.display_min_max(self.currentImage)
            elif self.mode == 1:
                self.currentImage = self.detect_change_contours(self.currentImage)

            self.error = False
        except Exception as e:
            logging.debug('update error')
            logging.exception(e)
            self.hiResCapture = PiRGBArray(self.camera)
            self.lowResCapture = PiRGBArray(self.camera, size=(self.safe_width(self.config["cv_width"]),
                                                               self.safe_height(self.config["cv_height"])))
            self.error = True
            pass

    def get_current_image(self):
        return self.currentImage

    @staticmethod
    def safe_width(width):
        div = width % 32
        if div is 0:
            return width
        else:
            logging.info("width " + str(width) + " not divisible by 32 trying " + str(width + 1))
            return ChangeDetector.safe_width(width+1)

    @staticmethod
    def safe_height(height):
        div = height % 16
        if div is 0:
            return height
        else:
            logging.info("height " + str(height) +" not divisible by 16 trying " + str(height+1))
            return ChangeDetector.safe_height(height+1)


