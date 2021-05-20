from naturewatch_camera_server.Publisher import Publisher
from subprocess import check_call
import threading
import os
import os.path
import pathlib
import datetime
import subprocess

class TelegramPublisher(Publisher):

    def __init__(self, bot, config, logger):
        super().__init__()
        self.config = config
        self.logger = logger
        self.bot = bot

        # The semaphore number sets how many publishing tasks to do at the same time.
        # Since FFmpeg is multi-threaded, there's no benefit in running more than one at the same time.
        # Also the high load can make the detection logic fail.
        # Increase it at your own risk.
        self.ffmpegSemaphore = threading.Semaphore(1)

    def doPublish(self, video_file_name, thumb_file_name):
        with self.ffmpegSemaphore:
            # The original video is 17-18MB big, too heavy to be easily shared.
            self.logger.info("Shrinking video for publishing: " + video_file_name)
                        
            if (canDoSoftwareEncoding()):
                (width, height) = (960, 540)
                encoder_options = [
                    "-crf", "25"
                ]
            else:
                (width, height) = (384, 216)
                encoder_options = [
                    "-c:v", "h264_omx",
                    "-profile:v", "main",
                    "-b:v", "450000"
                ]

            ffmpeg_cmdline = ["ffmpeg", "-hide_banner", "-nostats"]
            if (canUseHardwareDecoding()):
                ffmpeg_cmdline.extend(["-c:v", "h264_mmal"])
            ffmpeg_cmdline.extend([
                "-i", video_file_name,
                "-vf", f"scale={width}:{height}"
            ])
            ffmpeg_cmdline.extend(encoder_options)

            shrunk_file_name = video_file_name.replace(".mp4", "_shrunk.mp4")
            ffmpeg_cmdline.append(shrunk_file_name)
            
            self.logger.info("ffmpeg cmdline: " + " ".join(ffmpeg_cmdline))

            try:
                check_call(ffmpeg_cmdline)

                with open(shrunk_file_name, 'rb') as video_file:
                    with open(thumb_file_name, 'rb') as thumbnail_file:
                        self.logger.info("sending video file")
                        self.bot.send_video(video_file, thumbnail_file, width, height)
                        self.logger.info("send completed")
            finally:
                if os.path.isfile(shrunk_file_name):      
                    os.remove(shrunk_file_name)

            video_path = pathlib.Path(video_file_name)
            creation_time = datetime.datetime.fromtimestamp(video_path.stat().st_ctime)
            time = creation_time.strftime("%d/%m/%Y %H:%M:%S")
            self.bot.send_message(f"New video taken at {time} ⬆️")

    def publish_image(self, file_name):
        pass

    def publish_video(self, video_file_name, thumb_file_name):
        if self.bot is None:
            return

        thread = threading.Thread(target=self.doPublish, args=(video_file_name, thumb_file_name))
        self.logger.info("Will publish using thread " + str(thread))
        thread.start()

def canUseHardwareDecoding():
    vcgencmd_result = subprocess.run(['/opt/vc/bin/vcgencmd', 'get_mem', 'gpu'], stdout=subprocess.PIPE)
    result_text = vcgencmd_result.stdout.decode('utf-8').strip()
    properties = dict(pair.split('=') for pair in result_text.split(' '))
    gpu_mem_text = properties['gpu']
    gpu_mem = int(gpu_mem_text[:-1]) # assume M at the end as megabytes
    return gpu_mem >= 192

def canDoSoftwareEncoding():
    """
    Returns True if the device is powerful enough to encode video in software.
    Software encoding can be constant-quality, while hardware encoding (h264_omx)
    only allows constant-bitrate and the video has worse quality for the same
    average bitrate.
    """

    # Simple benchmark check: ffmpeg software decoder uses all cores, the more the merrier
    return os.cpu_count() >= 4