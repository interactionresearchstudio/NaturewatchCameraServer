from threading import Thread
import datetime
import cv2
import io
import logging
import os
from subprocess import call
try:
    import picamera
    import picamera.array
    picamera_exists = True
except ImportError:
    picamera = None
    picamera_exists = False


class FileSaver(Thread):

    def __init__(self, config, logger=None):
        super(FileSaver, self).__init__()

        if logger is not None:
            self.logging = logger
        else:
            self.logging = logging

        self.config = config

    def save_image(self, image):
        """
        Save image to disk
        :param image: numpy array image
        :return: filename
        """
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"
        self.logging.info('saving file')
        try:
            cv2.imwrite(os.path.join(self.config["photos_path"], filename), image)
            return filename
        except Exception as e:
            self.logging.error('FileSaver: save_photo() error: ')
            self.logging.exception(e)
            pass

    def save_video(self, stream):
        """
        Save raw video stream to disk
        :param stream: raw picamera stream object
        :return: none
        """
        self.logging.info('FileSaver: Writing video...')
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filenameMp4 = filename
        filename = filename + ".h264"
        filenameMp4 = filenameMp4 + ".mp4"
        stream.copy_to(os.path.join(self.config["videos_path"], filename))
        self.logging.info('FileSaver: Done writing video ' + filename)
        input_video = os.path.join(self.config["videos_path"], filename)
        output_video = os.path.join(self.config["videos_path"], filenameMp4)
        call(["MP4Box", "-fps", "25", "-add", input_video, output_video])
        os.remove(os.path.join(self.config["videos_path"], filename))
        self.logging.info('Removed ' + filename)



