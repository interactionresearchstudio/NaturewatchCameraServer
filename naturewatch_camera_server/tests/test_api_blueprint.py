import pytest
import sys
import json
from naturewatch_camera_server import create_app


@pytest.fixture()
def test_client():
    app = create_app()
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


def test_get_settings(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/settings' is requested (GET)
    THEN check the settings object is valid
    """
    response = test_client.get('/api/settings')
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert "rotation" in response_dict
    assert "exposure" in response_dict
    assert "sensitivity" in response_dict
    assert response_dict["sensitivity"] == "default"
    assert response_dict["exposure"]["mode"] == 'auto'
    assert response_dict["exposure"]["iso"] == 'auto'
    assert response_dict["exposure"]["shutter_speed"] == 0
    assert response_dict["rotation"] is False


def test_post_settings(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/settings' is requested (POST)
    THEN the settings object should be updated
    """
    settings = {
        "rotation": True,
        "exposure": {
            "mode": "auto",
        },
        "sensitivity": "less"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = test_client.post('/api/settings', data=json.dumps(settings), headers=headers)
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert "rotation" in response_dict
    assert "exposure" in response_dict
    assert "sensitivity" in response_dict
    assert response_dict["sensitivity"] == "less"
    assert response_dict["exposure"]["mode"] == 'auto'
    assert response_dict["exposure"]["iso"] == 'auto'
    assert response_dict["exposure"]["shutter_speed"] == 0
    assert response_dict["rotation"] is True


def test_session_status(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/session' is requested (GET)
    THEN the session status object should be returned
    """
    response = test_client.get('/api/session')
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert "time_started" in response_dict
    assert response_dict["mode"] == "inactive"


def test_session_start_photo(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/session/start/photo' is requested (POST)
    THEN photo session should start and new status object should be returned
    """
    response = test_client.post('/api/session/start/photo')
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert "time_started" in response_dict
    assert response_dict["mode"] == "photo"


def test_session_stop(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/session/stop' is requested (POST)
    THEN session should stop and new status object should be returned
    """
    response = test_client.post('/api/session/stop')
    assert response.status_code == 200
    response_dict = json.loads(response.data.decode('utf8'))
    assert "time_started" in response_dict
    assert response_dict["mode"] == "inactive"


def test_incorrect_time(test_client):
    """
    GIVEN a Flask application
    WHEN '/api/time/<time_string>' is sent a bad time
    THEN system time should not be updated
    """
    response = test_client.post('/api/time/1234')
    assert response.status_code == 400
    response_dict = json.loads(response.data.decode('utf8'))
    assert "ERROR" in response_dict
    assert response_dict["ERROR"] == "1234"

