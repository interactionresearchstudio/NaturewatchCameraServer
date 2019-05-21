import pytest

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    # Expose the Werkzeug test client
    testing_client = flask_app.test_client()

    # Establish application context
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

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