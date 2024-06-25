from naturewatch_camera_server import create_app, create_error_app
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Launch My Naturewatch Camera')
parser.add_argument('-p', action='store', dest='port', default=5000,
                    help='Port number to attach to')
args = parser.parse_args()

class CameraNotFoundException(Exception):
    pass

def detect_camera():
    camcheck_process = subprocess.Popen(['libcamera-hello', '--list-cameras'], stdout=subprocess.PIPE, text=True)
    output, error = camcheck_process.communicate()
    return output.strip()

if __name__ == '__main__':
    try:
        app = create_app()
        app.camera_controller.start()
        app.change_detector.start()
    except Exception as e:
        if "Unable to connect to camera" in str(e):
            camcheck = detect_camera()
            if camcheck == "No cameras available!":
                e = CameraNotFoundException("Unable to access camera. Is the cable properly connected?")
            else:
                e = CameraNotFoundException("Unable to access camera. Here is the list of cameras detected:\n\n" + camcheck)

        app = create_error_app(e)

    app.run(debug=False, threaded=True, port=args.port, host='0.0.0.0')
