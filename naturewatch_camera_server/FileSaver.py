from threading import Thread
import cv2
import io
import logging
import os
import datetime
from subprocess import call
import zipfile

try:
    from picamera2 import Picamera2
    picamera_exists = True
except ImportError:
    Picamera2 = None
    picamera_exists = False


class FileSaver(Thread):

    def __init__(self, config, logger=None):
        super(FileSaver, self).__init__()

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging

        self.config = config

# Scaledown factor for thumbnail images

        self.thumbnail_factor = self.config["tn_width"] / self.config["img_width"]

    def checkStorage(self):
        # Disk information
        disk_root = self.getDf()
        out = disk_root[4].split('%')
        self.logger.debug('FileSaver: {} % of storage space used.'.format(str(out[0])))
        return int(out[0])

    @staticmethod
    def getDfDescription():
        df = os.popen("df -h /")
        i = 0
        while True:
            i = i + 1
            line = df.readline()
            if i == 1:
                return line.split()[0:6]

    @staticmethod
    def getDf():
        df = os.popen("df -h /")
        i = 0
        while True:
            i = i + 1
            line = df.readline()
            if i == 2:
                return line.split()[0:6]

    def save_image(self, image, timestamp):
        """
        Save image to disk
        :param image: numpy array image
        :param timestamp: formatted timestamp string
        :return: filename
        """
        if self.checkStorage() < 99:
            filename = timestamp
            filename = filename + ".jpg"
            self.logger.debug('FileSaver: saving file')
            try:
                cv2.imwrite(os.path.join(self.config["photos_path"], filename), image)
                self.logger.info("FileSaver: saved file to " + os.path.join(self.config["photos_path"], filename))
                return filename
            except Exception as e:
                self.logger.error('FileSaver: save_photo() error: ')
                self.logger.exception(e)
                pass
        else:
            self.logger.error('FileSaver: not enough space to save image')
            return None

    def save_thumb(self, image, timestamp, media_type):

        filename = "thumb_"
        filename = filename + timestamp
        filename = filename + ".jpg"
        self.logger.debug('FileSaver: saving thumb')
        try:
            if media_type in ["photo", "timelapse"]:
# TODO: Build a proper downscaling routine for the thumbnails
#                self.logger.debug('Scaling by a factor of {}'.format(self.thumbnail_factor))
#                thumb = cv2.resize(image, 0, fx=self.thumbnail_factor, fy=self.thumbnail_factor, interpolation=cv2.INTER_AREA)
                cv2.imwrite(os.path.join(self.config["photos_path"], filename), image)
                self.logger.info("FileSaver: saved thumbnail to " + os.path.join(self.config["photos_path"], filename))
            else:
                cv2.imwrite(os.path.join(self.config["videos_path"], filename), image)
            return filename
        except Exception as e:
            self.logger.error('FileSaver: save_photo() error: ')
            self.logger.exception(e)
            pass

    def create_video_filename(self, timestamp):
        """
        Generate filename and path for video
        :param timestamp: formatted timestamp string
        :return: filename
        """
        if self.checkStorage() < 99:
            self.logger.info('FileSaver: Writing video...')
            filename = timestamp
            filenameMp4 = filename
            filename = filename + ".h264"
            filenameMp4 = filenameMp4 + ".mp4"
            fullpath = os.path.join(self.config["videos_path"], filename)
            return filename, fullpath, filenameMp4
        else:
            self.logger.error('FileSaver: not enough space to save video')
            return None

    def H264_to_MP4(self, input_video, output_video):
        """
        Wrap H264 video file in an MP4 container
        :param input_video: H264 file to wrap
        :param output_video: MP4 file to output
        """
        self.logger.info('FileSaver: converting H264 video to MP4...')
        output_video = os.path.join(self.config["videos_path"], output_video) 
        call(["ffmpeg", "-r", str(self.config["frame_rate"]), "-i", input_video, "-vcodec", "copy", output_video])
        os.remove(input_video)
        self.logger.debug('FileSaver: removed interim file ' + input_video)           


    @staticmethod
    def download_all_video():
        timestamp = datetime.datetime.now()
        filename = "video_"+timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename.strip()
        return filename

    def download_zip(self, filename):
        input_file = os.path.join(self.config["videos_path"], filename)
        output_zip = input_file + ".zip"
        zf = zipfile.ZipFile(output_zip, mode='w')
        try:
            self.logger.info('FileSaver: adding file')
            zf.write(input_file, os.path.basename(input_file))
        finally:
            self.logger.info('FileSaver: closing')
            zf.close()
        return output_zip
