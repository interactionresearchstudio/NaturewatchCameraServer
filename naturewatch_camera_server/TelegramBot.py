from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import socket

class TelegramBot():
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

        api_key = self.config["telegram_api_key"]
        self.chat_id = self.config['telegram_chat_id']

        self.updater = Updater(api_key)

        self.logger.info("Starting Telegram publisher")
        self.updater.start_polling()
        
        self.logger.info("Telegram publisher started")
        
        url = "http://%s" % (getLocalAddress())
        self.send_message(f"I'm ready\\. Go to [my webpage]({url}) to start capture\\.")

    def send_video(self, video_file, thumbnail_file, width, height):
        self.updater.bot.send_video(
            chat_id=self.chat_id,
            video=video_file,
            thumb=thumbnail_file,
            width=width,
            height=height,
            supports_streaming=True)

    def send_message(self, text):
        self.updater.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2
        )

def getLocalAddress():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
