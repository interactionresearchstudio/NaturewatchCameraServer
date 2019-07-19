from threading import Thread
import datetime
import cv2
import io
import logging
import os


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
        filename = filename + ".h264"
        with stream.lock:
            for frame in stream.frames:
                if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                    stream.seek(frame.position)
                    break

            with io.open("videos/" + filename, 'wb') as output:
                output.write(stream.read())
                self.logging.info('"FileSaver: Done writing video ' + filename)
