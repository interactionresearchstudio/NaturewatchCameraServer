from flask import Blueprint, Response, request, json
from flask import current_app
import time
import json

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


@api.route('/frame')
def frame():
    current_app.logger.info("Requested camera frame.")
    return Response(generate_jpg(current_app.camera_controller))


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
        # TODO send a error.jpg image as the frame instead.
        current_app.logger.warning("Could not retrieve image binary.")
        current_app.logger.exception(e)
        return b'Empty'


@api.route('/settings', methods=['GET', 'POST'])
def settings_handler():
    """
    Settings endpoint
    :return: settings json object
    """
    if request.method == 'GET':
        settings = construct_settings_object(current_app.camera_controller, current_app.change_detector)
        return Response(json.dumps(settings), mimetype='application/json')
    elif request.method == 'POST':
        settings = request.json
        if "rotation" in settings:
            current_app.camera_controller.set_camera_rotation(settings["rotation"])
        if "sensitivity" in settings:
            current_app.change_detector.set_sensitivity(settings["sensitivity"]["min"], settings["sensitivity"]["max"])
        if "mode" in settings["exposure"]:
            if settings["exposure"]["mode"] == "auto":
                current_app.camera_controller.auto_exposure()
        elif "shutter_speed" in settings and "iso" in settings:
            current_app.camera_controller.set_exposure(settings["exposure"]["shutter_speed"],
                                                       settings["exposure"]["iso"])
        new_settings = construct_settings_object(current_app.camera_controller, current_app.change_detector)
        return Response(json.dumps(new_settings), mimetype='application/json')


def construct_settings_object(camera_controller, change_detector):
    """
    Construct a dictionary populated with the current settings of the camera controller and change detector.
    :param camera_controller: Running camera controller object
    :param change_detector: Running change detector object
    :return: settings dictionary
    """
    settings = {
        "rotation": camera_controller.rotated_camera,
        "exposure": {
            "mode": camera_controller.get_exposure_mode(),
            "iso": camera_controller.get_iso(),
            "shutter_speed": camera_controller.get_shutter_speed(),
        },
        "sensitivity": {
            "min": change_detector.minWidth,
            "max": change_detector.maxWidth
        }
    }
    return settings


@api.route('/session')
def get_session():
    """
    Get session status
    :return: session status json object
    """
    session_status = {
        "mode": current_app.change_detector.mode,
        "time_started": current_app.change_detector.session_start_time
    }
    return Response(json.dumps(session_status), mimetype='application/json')
