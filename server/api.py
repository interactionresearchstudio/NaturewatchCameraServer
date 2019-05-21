from flask import Blueprint, Response
from flask import current_app
from CameraController import camera_controller

api = Blueprint('api', __name__)


@api.route('/feed')
def feed():
    """
    Feed endpoint
    :return: mjpg content
    """
    current_app.logger.info("Serving camera feed...")
    return Response(generate_mjpg(), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_mjpg():
    """
    Generate mjpg response using camera_controller
    :return: Yield string with jpeg byte array and content type
    """
    while camera_controller.is_alive():
        try:
            frame = camera_controller.get_image_binary()
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
        except BrokenPipeError:
            current_app.logger.info("Client disconnected from camera feed.")
            break
        except ConnectionResetError:
            current_app.logger.info("Camera feed connection reset by peer.")
            break
