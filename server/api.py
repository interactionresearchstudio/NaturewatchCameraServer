from flask import Blueprint, Response
from flask import current_app
import time
# from CameraController import camera_controller

api = Blueprint('api', __name__)


@api.route('/feed')
def feed():
    """
    Feed endpoint
    :return: mjpg content
    """
    current_app.logger.info("Serving camera feed...")
    with current_app.app_context():
        return Response(generate_mjpg(current_app.camera_controller),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@api.route('/frame')
def frame():
    current_app.logger.info("Requested camera frame.")
    return Response(generate_jpg(current_app.camera_controller))


def generate_mjpg(camera_controller):
    """
    Generate mjpg response using camera_controller
    :return: Yield string with jpeg byte array and content type
    """
    while camera_controller.is_alive() is False:
        camera_controller.start()
        time.sleep(1)
    while True:
        latest_frame = camera_controller.get_image_binary()
        response = b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bytearray(latest_frame) + b'\r\n'
        yield(response)


def generate_jpg(camera_controller):
    """
    Generate jpg response once.
    :return: String with jpeg byte array and content type
    """
    # Start camera controller if it hasn't been started already.
    while camera_controller.is_alive() is False:
        camera_controller.start()
        time.sleep(1)
    try:
        latest_frame = camera_controller.get_image_binary()
        response = b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bytearray(latest_frame) + b'\r\n'
        return response
    except Exception as e:
        current_app.logger.warning("Could not retrieve image binary.")
        current_app.logger.exception(e)
        return b'Empty'
