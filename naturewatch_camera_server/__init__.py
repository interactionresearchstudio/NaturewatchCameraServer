#!../venv/bin/python
import json
import logging
from naturewatch_camera_server.Publisher import DummyPublisher
from naturewatch_camera_server.TelegramBot import TelegramBot
import os
import sys
from shutil import copyfile
from logging.handlers import RotatingFileHandler
from naturewatch_camera_server.CameraController import CameraController
from naturewatch_camera_server.ChangeDetector import ChangeDetector
from naturewatch_camera_server.FileSaver import FileSaver
from naturewatch_camera_server.TelegramPublisher import TelegramPublisher
from flask import Flask
from naturewatch_camera_server.api import api
from naturewatch_camera_server.data import data
from naturewatch_camera_server.static_page import static_page


def create_app():
    """
    Create flask app
    :return: Flask app object
    """
    flask_app = Flask(__name__, static_folder="static/client/build")
    flask_app.register_blueprint(api, url_prefix='/api')
    flask_app.register_blueprint(data, url_prefix='/data')
    flask_app.register_blueprint(static_page)

    # Setup logger
    flask_app.logger = logging.getLogger(__name__)
    flask_app.logger.setLevel(logging.DEBUG)
    # setup logging handler for stderr
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.INFO)
    flask_app.logger.addHandler(stderr_handler)

    # Load configuration json
    module_path = os.path.abspath(os.path.dirname(__file__))
    flask_app.logger.info("Module path: " + module_path)
    # load central config file first
    flask_app.user_config = json.load(open(os.path.join(module_path, "config.json")))

    # Check if a config file exists in data directory
    if os.path.isfile(os.path.join(module_path, flask_app.user_config["data_path"], 'config.json')):
        # if yes, load that file, too
        flask_app.logger.info("Using config file from data context")
        flask_app.user_config = json.load(open(os.path.join(module_path,
                                                            flask_app.user_config["data_path"],
                                                            'config.json')))
    else:
        # if not, copy central config file to data directory
        flask_app.logger.warning("Config file does not exist within the data context, copying file")
        copyfile(os.path.join(module_path, "config.json"),
                 os.path.join(module_path, flask_app.user_config["data_path"], "config.json"))

    # Set up logging to file
    file_handler = logging.handlers.RotatingFileHandler(os.path.join(module_path, flask_app.user_config["data_path"], 'camera.log'), maxBytes=1024000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    numeric_loglevel = getattr(logging, flask_app.user_config["log_level"].upper(), None)
    if not isinstance(numeric_loglevel, int):
        flask_app.logger.info('Invalid log level {0} in config file: %s'.format(self.config["log_level"]))
    else:
        file_handler.setLevel(numeric_loglevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    flask_app.logger.addHandler(file_handler)
    flask_app.logger.info("Logging to file initialised")

    # Find photos and videos paths
    flask_app.user_config["photos_path"] = os.path.join(module_path, flask_app.user_config["photos_path"])
    flask_app.logger.info("Photos path: " + flask_app.user_config["photos_path"])
    if os.path.isdir(flask_app.user_config["photos_path"]) is False:
        os.mkdir(flask_app.user_config["photos_path"])
        flask_app.logger.warning("Photos directory does not exist, creating path")
    flask_app.user_config["videos_path"] = os.path.join(module_path, flask_app.user_config["videos_path"])
    if os.path.isdir(flask_app.user_config["videos_path"]) is False:
        os.mkdir(flask_app.user_config["videos_path"])
        flask_app.logger.warning("Videos directory does not exist, creating path")

    # Instantiate classes
    flask_app.logger.debug("Instantiating classes ...")
    flask_app.camera_controller = CameraController(flask_app.logger, flask_app.user_config)
    try:
        flask_app.telegram_bot = TelegramBot(flask_app.logger, flask_app.user_config)
        flask_app.publisher = TelegramPublisher(flask_app.telegram_bot, flask_app.user_config, flask_app.logger)
    except KeyError:
        flask_app.logger.info("Telegram API key or chat ID not found, won't publish")
        flask_app.publisher = DummyPublisher()
    except:
        flask_app.logger.exception("Unable to start Telegram publisher")
        flask_app.publisher = DummyPublisher()

    flask_app.change_detector = ChangeDetector(
        flask_app.camera_controller, 
        flask_app.publisher,
        flask_app.user_config, 
        flask_app.logger
    )
    flask_app.file_saver = FileSaver(flask_app.user_config, flask_app.logger)

    flask_app.logger.debug("Initialisation finished")
    return flask_app

def create_error_app(e):
    """
    Create flask app about an error occurred in the main app
    :return: Flask app object
    """
    flask_app = Flask(__name__, static_folder="static/client/build")

    @flask_app.route('/')
    def index():
        return f"<html><body><h1>Unable to start NaturewatchCameraServer.</h1>An error occurred:<pre>{e}</pre></body></html>"

    return flask_app
