import pytest
import sys
import json
import os
import time
from naturewatch_camera_server import create_app
from naturewatch_camera_server.FileSaver import FileSaver

app = create_app()
file_saver = FileSaver()


@pytest.fixture(autouse=True)
def run_around_tests():
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
    filename = file_saver.save_image(app.camera_controller.get_image())
    assert os.path.isfile(filename)
    assert os.path.getsize(filename) != 0
    os.remove(filename)
