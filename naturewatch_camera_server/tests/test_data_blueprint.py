import pytest
import sys
import json
import time
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

    for x in range(4):
        filename = file_saver.save_image(app.camera_controller.get_image())
        photos_list.append(filename)
        time.sleep(1)

    yield testing_client

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
