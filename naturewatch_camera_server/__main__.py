from naturewatch_camera_server import create_app

if __name__ == '__main__':
    app = create_app()
    app.camera_controller.start()
    app.run(debug=False, threaded=True)
