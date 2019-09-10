import pytest
import sys
import json
import time
import datetime
import os
from naturewatch_camera_server import create_app
from naturewatch_camera_server.FileSaver import FileSaver

photos_list = list()


@pytest.fixture()
def test_client():
    global photos_list
    app = create_app()
    testing_client = app.test_client()

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    file_saver = FileSaver(app.user_config)

    while app.camera_controller.is_alive() is False:
        app.camera_controller.start()
        time.sleep(1)

    for x in range(2):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = file_saver.save_image(app.camera_controller.get_image(), timestamp)
        photos_list.append(filename)
        time.sleep(1)

    yield testing_client

    # Teardown

    for f in photos_list:
        os.remove(app.user_config["photos_path"] + f)

    photos_list = list()

    app.camera_controller.stop()

    ctx.pop()


def test_photos(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/photos' is requested (GET)
    THEN list of photos should be returned.
    """
    response = test_client.get('/data/photos')
    assert response.status_code == 200
    response_list = json.loads(response.data.decode('utf8'))
    assert isinstance(response_list, list)
    for f in photos_list:
        assert f in response_list


def test_photo(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/photo/<photo>' is requested (GET)
    THEN a single photo should be returned.
    """
    response = test_client.get('/data/photos/' + photos_list[0])
    assert response.status_code == 200


def test_delete_photo(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/photo/<photo>' is requested (GET)
    THEN a single photo should be returned.
    """
    response = test_client.delete('/data/photos/' + photos_list[0])
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert response_dict["SUCCESS"] == photos_list[0]
    del photos_list[0]
