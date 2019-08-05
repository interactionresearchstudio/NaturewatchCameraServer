from threading import Thread
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

    def save_image(self, image,timestamp):
        """
        Save image to disk
        :param image: numpy array image
        :return: filename
        """

        filename = timestamp
        filename = filename + ".jpg"
        self.logging.info('saving file')
        try:
            cv2.imwrite(os.path.join(self.config["photos_path"], filename), image)
            return filename
        except Exception as e:
            self.logging.error('FileSaver: save_photo() error: ')
            self.logging.exception(e)
            pass

    def save_thumb(self,image,timestamp,format):

        filename = "thumb_"
        filename = filename + timestamp
        filename = filename + ".jpg"
        self.logging.info('saving thumb')
        try:
            if format is "photo":
                cv2.imwrite(os.path.join(self.config["photos_path"], filename), image)
            else:
                cv2.imwrite(os.path.join(self.config["videos_path"], filename), image)
            return filename
        except Exception as e:
            self.logging.error('FileSaver: save_photo() error: ')
            self.logging.exception(e)
            pass


    def save_video(self, stream,timestamp):
        """
        Save raw video stream to disk
        :param stream: raw picamera stream object
        :return: none
        """
        self.logging.info('FileSaver: Writing video...')
        filename = timestamp
        filenameMp4 = filename
        filename = filename + ".h264"
        filenameMp4 = filenameMp4 + ".mp4"
        stream.copy_to(os.path.join(self.config["videos_path"], filename),seconds = self.config["video_duration_before_motion"] + self.config["video_duration_after_motion"])
        self.logging.info('FileSaver: Done writing video ' + filename)
        input_video = os.path.join(self.config["videos_path"], filename)
        output_video = os.path.join(self.config["videos_path"], filenameMp4)
        call(["MP4Box", "-fps", str(self.config["frame_rate"]), "-add", input_video, output_video])
        os.remove(os.path.join(self.config["videos_path"], filename))
        self.logging.info('Removed ' + filename)



