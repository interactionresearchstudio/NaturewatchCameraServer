from naturewatch_camera_server import create_app

if __name__ == '__main__':
    app = create_app()
    app.camera_controller.start()
    app.change_detector.start()
    app.run(debug=False, threaded=True, port=5000, host='0.0.0.0')
