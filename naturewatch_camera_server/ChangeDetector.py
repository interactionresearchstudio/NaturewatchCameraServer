import cv2
import numpy as np
from threading import Thread
from datetime import datetime
import time
import imutils
import logging
from naturewatch_camera_server.FileSaver import FileSaver


class ChangeDetector(Thread):

    def __init__(self, camera_controller, config, logger):
        super(ChangeDetector, self).__init__()
        self.config = config
        self.daemon = True
        self.cancelled = False
        self.camera_controller = camera_controller
        self.logger = logger
        self.file_saver = FileSaver(self.config, logger=self.logger)
        self.sensitivity = self.config["sensitivity"]
        self.device_time = None
        self.device_time_start = None
        self.mode = "inactive"
        self.session_start_time = None
        self.lastPhotoTime = self.get_fake_time()
        self.previmg = None
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

    def detect_change(self, previmg, curimg):
        """
        Detect changes in frame
        :param previmg: previous image
        :param curimg: current image
        :return: True if it's time to capture
        """
        if previmg is not None:
            # Measure pixels differences between current and previous frame
            mse = np.square(np.subtract(curimg, previmg)).mean()
            if mse > self.sensitivity:
                if self.get_fake_time() - self.lastPhotoTime >= self.config['min_photo_interval_s']:
                    self.logger.info('ChangeDetector: Motion detected and capture triggered (mse={})'.format(mse))
                    return True
                else:
                    return False
            # This next line is useful for determining appropriate sensitivity levels
            elif mse > 1.5:
                    self.logger.info('ChangeDetector: Motion detected (mse={})'.format(mse))
                    return False
            else:
                return False

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity
        self.logger.info('ChangeDetector: Sensitivity set to {}'.format(self.sensitivity))

    def start_photo_session(self):
        self.camera_controller.run_autofocus()
        self.logger.info('ChangeDetector: starting photo capture mode')
        self.mode = "photo"
        self.session_start_time = self.get_fake_time()

    def start_video_session(self):
        self.camera_controller.run_autofocus()
        self.logger.info('ChangeDetector: starting video capture mode')
        self.mode = "video"
        self.output = self.camera_controller.start_video_stream()
        self.session_start_time = self.get_fake_time()

    def start_timelapse_session(self):
        self.camera_controller.run_autofocus()
        self.logger.info('ChangeDetector: starting timelapse capture mode')
        self.mode = "timelapse"
        self.session_start_time = self.get_fake_time()
          
    def stop_session(self):
        self.logger.info('ChangeDetector: ending capture mode')
        if self.mode == "video":
            self.camera_controller.stop_video_stream()
        elif self.mode == "photo" or self.mode == "timelapse":
            pass
        self.mode = "inactive"
        self.camera_controller.recording_active = False

# TODO: whether to use the video-port or not does not directly depend on the mode
# In case video is requested, the video port will always be used for both resolutions
# In case photo is requested, the video port can be used, but need not. It should be left a matter of configuration
    def update(self):
        time.sleep(0.03)
        # only check for motion while a session is active and a recording isn't already in progress
        if self.mode in ["photo", "video"] and self.camera_controller.recording_active is False:
            # get an md image
            yuvimg = self.camera_controller.get_md_yuvimage()
            # only proceed if there is an image
            if yuvimg is not None:
                if self.detect_change(self.previmg, yuvimg) is True:
                    self.logger.info('ChangeDetector: detected motion. Saving...')
                    timestamp = self.get_formatted_time()
                    self.camera_controller.recording_active = True
                    if self.mode == "photo":
                        image = self.camera_controller.get_hires_image()
                        self.file_saver.save_image(image, timestamp)
                        self.file_saver.save_thumb(imutils.resize(image, width=self.config["md_width"]), timestamp, self.mode)
                        self.lastPhotoTime = self.get_fake_time()
                        self.logger.info('ChangeDetector: photo capture completed')
                        yuvimg = None
                    elif self.mode == "video":
                        img = self.camera_controller.get_md_image()
                        self.file_saver.save_thumb(img, timestamp, self.mode)
                        filename, fullpath, filenameMp4 = self.file_saver.create_video_filename(timestamp)
                        self.camera_controller.start_saving_video(fullpath)
                        self.camera_controller.wait_recording(self.config["video_duration_after_motion"])
                        self.camera_controller.stop_saving_video()
                        self.file_saver.H264_to_MP4(fullpath, filenameMp4)
                        self.logger.info('ChangeDetector: video capture completed')
                        self.lastPhotoTime = self.get_fake_time()
                        self.logger.debug('ChangeDetector: video timer reset')
                        yuvimg = None
                    else:
        # TODO: Add debug code that logs a line every x seconds so we can see the ChangeDetector is still alive
        #            self.logger.debug('ChangeDetector: idle')
                        pass
                    self.camera_controller.recording_active = False
                self.previmg = yuvimg
            else:
                self.logger.error('ChangeDetector: not receiving any images for motion detection!')
                time.sleep(1)

        # TODO: implement periodic pictures
        elif self.mode == "timelapse":
            # take one picture every minute
            if self.get_fake_time() - self.lastPhotoTime >= self.timelapse:
                self.logger.info('ChangeDetector: ' + str(self.timelapse) + 's elapsed -> capturing...')
                # TODO: no magic numbers! (make it configurable)
                timestamp = self.get_formatted_time()
                image = self.camera_controller.get_hires_image()
                self.file_saver.save_image(image, timestamp)
                self.file_saver.save_thumb(imutils.resize(image, width=self.config["md_width"]), timestamp, self.mode)
                self.lastPhotoTime = self.get_fake_time()
                self.logger.info('ChangeDetector: photo capture completed')

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
