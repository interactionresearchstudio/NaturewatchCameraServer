from threading import Thread
import cv2
import io
import logging
import os
import datetime
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

    def checkStorage(self):
        # Disk information
        description = self.getDfDescription()
        disk_root = self.getDf()
        out = disk_root[4].split('%')
        return int(out[0])

    def getDfDescription(self):
        df = os.popen("df -h /")
        i = 0
        while True:
            i = i + 1
            line = df.readline()
            if i==1:
                return(line.split()[0:6])
                                 
    def getDf(self):
        df = os.popen("df -h /")
        i = 0
        while True:
            i = i + 1
            line = df.readline()
            if i==2:
                return(line.split()[0:6])


    def save_image(self, image,timestamp):
        """
        Save image to disk
        :param image: numpy array image
        :return: filename
        """
        if self.checkStorage() < 99 :
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
        else : 
            self.logging.error('not enough space to save image')
            return None

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

    def save_video(self, stream,timestamp,videoLength):
        """
        Save raw video stream to disk
        :param stream: raw picamera stream object
        :return: none
        """
        video_length = videoLength
        if videoLength > 15:
            video_length = 15
        else :
            video_length = videoLength
        if self.checkStorage() < 99 :
            self.logging.info('FileSaver: Writing video...')
            filename = timestamp
            filenameMp4 = filename
            filename = filename + ".h264"
            filenameMp4 = filenameMp4 + ".mp4"
            stream.copy_to(os.path.join(self.config["videos_path"], filename),seconds = video_length)
            self.logging.info('FileSaver: Done writing video ' + filename)
            input_video = os.path.join(self.config["videos_path"], filename)
            output_video = os.path.join(self.config["videos_path"], filenameMp4)
            call(["MP4Box", "-fps", str(self.config["frame_rate"]), "-add", input_video, output_video])
            os.remove(os.path.join(self.config["videos_path"], filename))
            self.logging.info('Removed ' + filename)
        else : 
            self.logging.error('not enough space to save video')
            return None
    
    def download_all_video(self):
        timestamp = datetime.datetime.now()
        filename = "video_"+timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename.strip()
        output_folder = os.path.join(self.config["data_path"], filename)
        call(["cp", "-r", "data/videos/", output_folder])
        call(["zip","-r",output_folder,output_folder])
        #call(["rm","-rf",output_folder])