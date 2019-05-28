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
    return Response(generate_mjpg(), mimetype='multipart/x-mixed-replace; boundary=frame')


@api.route('/frame')
def frame():
    current_app.logger.info("Requested camera frame.")
    return Response(generate_jpg())


def generate_mjpg():
    """
    Generate mjpg response using camera_controller
    :return: Yield string with jpeg byte array and content type
    """
    while current_app.camera_controller.is_alive():
        try:
            response = generate_jpg()
            yield(response)
        except BrokenPipeError:
            current_app.logger.info("Client disconnected from camera feed.")
            break
        except ConnectionResetError:
            current_app.logger.info("Camera feed connection reset by peer.")
            break


def generate_jpg():
    """
    Generate jpg response once.
    :return: String with jpeg byte array and content type
    """
    # Start camera controller if it hasn't been started already.
    while current_app.camera_controller.is_alive() is False:
        current_app.camera_controller.start()
        time.sleep(1)
    try:
        latest_frame = current_app.camera_controller.get_image_binary()
        response = b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bytearray(latest_frame) + b'\r\n'
        return response
    except Exception as e:
        current_app.logger.warning("Could not retrieve image binary.")
        current_app.logger.exception(e)
        return b'Empty'
