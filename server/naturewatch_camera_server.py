#!../venv/bin/python
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from CameraController import CameraController
from ChangeDetector import ChangeDetector
from flask import Flask
from api import api
from static_page import static_page


def create_app():
    """
    Create flask app
    :return: Flask app object
    """
    flask_app = Flask(__name__)
    flask_app.register_blueprint(api, url_prefix='/api')
    flask_app.register_blueprint(static_page)

    # Setup logger
    # handler = RotatingFileHandler('naturewatch_camera_server.log', maxBytes=10000, backupCount=1)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    flask_app.logger.addHandler(handler)

    # Load configuration json
    config = json.load(open(os.path.join(sys.path[0], "config.json")))

    # Instantiate classes
    flask_app.camera_controller = CameraController(use_splitter_port=True)
    flask_app.change_detector = ChangeDetector(flask_app.camera_controller, config, flask_app.logger)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.camera_controller.start()
    app.run(debug=True, threaded=True)
