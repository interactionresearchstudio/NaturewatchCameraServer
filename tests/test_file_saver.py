import pytest
import sys
import json
import os
sys.path.insert(0, './server')
from FileSaver import FileSaver
import naturewatch_camera_server

app = naturewatch_camera_server.create_app()
file_saver = FileSaver()


@pytest.fixture()
def test_client():
    testing_client = app.test_client()

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    app.camera_controller.stop()

    ctx.pop()


def test_image_save():
    filename = file_saver.save_image(app.camera_controller.get_image())
    assert os.path.isfile(filename)
    
