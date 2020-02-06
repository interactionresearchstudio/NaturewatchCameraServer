import pytest
import sys
import json
import time
import datetime
import os
from naturewatch_camera_server import create_app
from naturewatch_camera_server.FileSaver import FileSaver

photos_list = list()
videos_list = list()
photos_thumb_list = list()
videos_thumb_list = list()


@pytest.fixture(scope="session")
def test_client():
    global photos_list
    global videos_list
    app = create_app()
    testing_client = app.test_client()

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    file_saver = FileSaver(app.user_config)

    # Start camera controller
    while app.camera_controller.is_alive() is False:
        app.camera_controller.start()
        time.sleep(1)

    # Take photos and record their filenames
    for x in range(2):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        thumb = file_saver.save_thumb(app.camera_controller.get_md_image(), timestamp, "photo")
        filename = file_saver.save_image(app.camera_controller.get_hires_image(), timestamp)
        photos_list.append(filename)
        photos_thumb_list.append(thumb)
        time.sleep(1)

    # Record videos and save their filenames.
    app.camera_controller.start_video_stream()
    for y in range(2):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        time.sleep(2)
        thumb = file_saver.save_thumb(app.camera_controller.get_md_image(), timestamp, "video")
        app.camera_controller.wait_recording(2)
        with app.camera_controller.get_video_stream().lock:
            filename = file_saver.save_video(app.camera_controller.get_video_stream(), timestamp)
            videos_list.append(filename)
            videos_thumb_list.append(thumb)
            time.sleep(1)

    yield testing_client

    # Teardown

    for f in photos_list:
        os.remove(app.user_config["photos_path"] + f)
    for f in videos_list:
        os.remove(app.user_config["videos_path"] + f)
    for f in photos_thumb_list:
        os.remove(app.user_config["photos_path"] + f)
    for f in videos_thumb_list:
        os.remove(app.user_config["videos_path"] + f)

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
    global photos_list
    response = test_client.delete('/data/photos/' + photos_list[0])
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert response_dict["SUCCESS"] == photos_list[0]
    del photos_list[0]
    del photos_thumb_list[0]


def test_videos(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/videos' is requested (GET)
    THEN list of videos should be returned.
    """
    response = test_client.get('/data/videos')
    assert response.status_code == 200
    response_list = json.loads(response.data.decode('utf8'))
    assert isinstance(response_list, list)
    for f in videos_list:
        assert f in response_list


def test_video(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/video/<video>' is requested (GET)
    THEN a single video should be returned.
    """
    response = test_client.get('/data/videos/' + videos_list[0])
    assert response.status_code == 200


def test_delete_video(test_client):
    """
    GIVEN a Flask application
    WHEN '/data/video/<video>' is requested (GET)
    THEN a single video should be returned.
    """
    global videos_list
    response = test_client.delete('/data/videos/' + videos_list[0])
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert response_dict["SUCCESS"] == videos_list[0]
    del videos_list[0]
    del videos_thumb_list[0]
