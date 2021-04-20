from naturewatch_camera_server import create_app
import argparse

parser = argparse.ArgumentParser(description='Launch My Naturewatch Camera')
parser.add_argument('-p', action='store', dest='port', default=5000,
                    help='Port number to attach to')
args = parser.parse_args()

if __name__ == '__main__':
    try:
        app = create_app()
        app.camera_controller.start()
        app.change_detector.start()
    except e:
        app = create_error_app(e)

    app.run(debug=False, threaded=True, port=args.port, host='0.0.0.0')
