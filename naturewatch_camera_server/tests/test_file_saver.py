import pytest
import sys
import json
import os
import time
import datetime
from naturewatch_camera_server import create_app
from naturewatch_camera_server.FileSaver import FileSaver

file_saver = None
app = None


@pytest.fixture(autouse=True)
def run_around_tests():
    global file_saver
    global app
    app = create_app()
    file_saver = FileSaver(app.user_config)
    testing_client = app.test_client()

    while app.camera_controller.is_alive() is False:
        app.camera_controller.start()
        time.sleep(1)

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    app.camera_controller.stop()

    ctx.pop()


def test_image_save():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = file_saver.save_image(app.camera_controller.get_image(), timestamp)
    assert os.path.isfile(app.user_config["photos_path"] + filename)
    assert os.path.getsize(app.user_config["photos_path"] + filename) != 0
    os.remove(app.user_config["photos_path"] + filename)
