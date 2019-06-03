import pytest
import sys
import json
sys.path.insert(0, './server')
import naturewatch_camera_server


@pytest.fixture()
def test_client():
    app = naturewatch_camera_server.create_app()
    testing_client = app.test_client()

    # Establish application context
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    app.camera_controller.stop()

    ctx.pop()


def test_root_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"My Naturewatch Camera" in response.data

def test_jpg(test_client):
    """
    GIVEN a Flask application
    WHEN the '/api/frame' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/api/frame')
    assert response.status_code == 200
    assert b"Content-Type: image/jpeg" in response.data

def test_mjpg(test_client):
    """
    GIVEN a Flask application
    WHEN the '/api/feed' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/api/feed')
    assert response.status_code == 200
    # TODO test actual stream
