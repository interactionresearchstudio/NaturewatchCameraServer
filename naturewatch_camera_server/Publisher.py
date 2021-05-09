from telegram.ext import Updater, CommandHandler
import logging

class Publisher():

    def __init__(self, config, logger=None):
        self.config = config

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging

        self.updater = Updater(self.config["telegram_api_key"])
        # dp = updater.dispatcher
        self.logger.info("Starting Telegram publisher")
        # dp.add_handler(CommandHandler('bop',bop))
        self.updater.start_polling()
        self.logger.info("Telegram publisher started")

    def publish_image(self, file_name):
        pass

    def publish_video(self, video_file_name, thumb_file_name):
        self.logger.info("Publishing video in " + video_file_name + " with thumbnail " + thumb_file_name)
        with open(video_file_name, 'rb') as video_file:
            with open(thumb_file_name, 'rb') as thumbnail_file:
                self.logger.info("sending video file")
                self.updater.bot.send_video(
                    chat_id=self.config['telegram_chat_id'],
                    video=video_file,
                    thumb=thumbnail_file,
                    width=1920,
                    height=1080,
                    supports_streaming=True)
                self.logger.info("send completed")