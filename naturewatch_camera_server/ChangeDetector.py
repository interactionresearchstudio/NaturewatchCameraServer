import cv2
import numpy as np
from threading import Thread
from datetime import datetime
import time
import imutils
import logging
from naturewatch_camera_server.FileSaver import FileSaver
from naturewatch_camera_server.Publisher import Publisher


class ChangeDetector(Thread):

    def __init__(self, camera_controller, config, logger):
        super(ChangeDetector, self).__init__()
        self.config = config
        self.daemon = True
        self.cancelled = False

        self.camera_controller = camera_controller

        self.logger = logger

        self.file_saver = FileSaver(self.config, logger=self.logger)
        self.publisher = Publisher(self.config, logger=self.logger)

        self.minWidth = self.config["min_width"]
        self.maxWidth = self.config["max_width"]
        self.minHeight = self.config["min_height"]
        self.maxHeight = self.config["max_height"]

        self.device_time = None
        self.device_time_start = None

        self.mode = "inactive"
        self.session_start_time = None
        self.avg = None
        self.lastPhotoTime = self.get_fake_time()
        self.numOfPhotos = 0

        self.activeColour = (255, 255, 0)
        self.inactiveColour = (100, 100, 100)
        self.isMinActive = False
        self.currentImage = None

        self.timelapse_active = False
        self.timelapse        = self.config["default_timelapse"]

        self.logger.info("ChangeDetector: initialised")

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
        self.camera_controller.stop()

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
            self.logger.error('ChangeDetector: save_photo() error: ')
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
            return False

        # add to accumulation model and find the change
        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold, dilate and find contours
        thresh = cv2.threshold(frame_delta, self.config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        largest_contour = self.get_largest_contour(cnts)

        if largest_contour is None:
            return False

        (x, y, w, h) = cv2.boundingRect(largest_contour)

        # if the contour is too small, return false
        if w > self.maxWidth or w < self.minWidth or h > self.maxHeight or h < self.minHeight:
            return False
        else:
            if self.get_fake_time() - self.lastPhotoTime >= self.config['min_photo_interval_s']:
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
        self.logger.info('ChangeDetector: starting photo capture')
        self.mode = "photo"
        self.session_start_time = self.get_fake_time()

    def start_video_session(self):
        self.logger.info('ChangeDetector: starting video capture')
        self.mode = "video"
        self.camera_controller.start_video_stream()
        self.session_start_time = self.get_fake_time()

    def start_timelapse_session(self):
        self.logger.info('ChangeDetector: starting timelapse capture')
        self.mode = "timelapse"
        self.session_start_time = self.get_fake_time()
        
        
    def stop_session(self):
        self.logger.info('ChangeDetector: ending capture')
        if self.mode == "video":
            self.camera_controller.stop_video_stream()
        elif self.mode == "photo" or self.mode == "timelapse":
            pass
        self.mode = "inactive"

# TODO: whether to use the video-port or not does not directly depend on the mode
# In case video is requested, the video port will always be used for both resolutions
# In case photo is requested, the video port can be used, but need not. It should be left a matter of configuration
    def update(self):
        time.sleep(0.02)
        # only check for motion while a session is active
        if self.mode in ["photo", "video"]:
            # get an md image
            img = self.camera_controller.get_md_image()
            # only proceed if there is an image
            if img is not None:
                if self.detect_change_contours(img) is True:
                    self.logger.info("ChangeDetector: detected motion. Starting capture...")
                    try:
                        timestamp = self.get_formatted_time()
                        if self.mode == "photo":
                            image = self.camera_controller.get_hires_image()
                            self.file_saver.save_image(image, timestamp)
                            self.file_saver.save_thumb(imutils.resize(image, width=self.config["md_width"]), timestamp, self.mode)
                            self.lastPhotoTime = self.get_fake_time()
                            self.logger.info("ChangeDetector: photo capture completed")
                        elif self.mode == "video":
                            thumb_file = self.file_saver.save_thumb(img, timestamp, self.mode)
                            self.camera_controller.wait_recording(self.config["video_duration_after_motion"])
                            self.logger.info("ChangeDetector: video capture completed")
                            with self.camera_controller.get_video_stream().lock:
                                video_file = self.file_saver.save_video(self.camera_controller.get_video_stream(), timestamp)
                            self.lastPhotoTime = self.get_fake_time()
                            self.logger.debug("ChangeDetector: video timer reset")
                            self.publisher.publish_video(video_file, thumb_file)
                        else:
            # TODO: Add debug code that logs a line every x seconds so we can see the ChangeDetector is still alive
            #            self.logger.debug("ChangeDetector: idle")
                            pass
                    except Exception as e:
                        self.logger.exception('Error during/after capture')

            else:
                self.logger.error("ChangeDetector: not receiving any images for motion detection!")
                time.sleep(1)

        # TODO: implement periodic pictures
        elif self.mode == "timelapse":
            # take one picture every minute
            if self.get_fake_time() - self.lastPhotoTime >= self.timelapse:
                self.logger.info("ChangeDetector: " + str(self.timelapse) + "s elapsed -> capturing...")
                # TODO: no magic numbers! (make it configurable)
                timestamp = self.get_formatted_time()
                image = self.camera_controller.get_hires_image()
                self.file_saver.save_image(image, timestamp)
                self.file_saver.save_thumb(imutils.resize(image, width=self.config["md_width"]), timestamp, self.mode)
                self.lastPhotoTime = self.get_fake_time()
                self.logger.info("ChangeDetector: photo capture completed")

    def get_fake_time(self):
        if self.device_time is not None:
            time_float = self.device_time + time.time() - self.device_time_start
        else:
            time_float = time.time()
        return time_float

    def get_formatted_time(self):
        time_float = self.get_fake_time()
        timestamp = datetime.utcfromtimestamp(time_float).strftime('%Y-%m-%d-%H-%M-%S')
        return timestamp
