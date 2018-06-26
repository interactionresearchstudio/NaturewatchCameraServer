#!/usr/bin/env python
import json
import cv2
import os
import imutils
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from ChangeDetector import ChangeDetector

os.chdir("/home/pi/NaturewatchCameraServer")
config = json.load(open("config.json"))
os.chdir("/home/pi/NaturewatchCameraServer/www")

# NatureCam implementation
changeDetectorInstance = ChangeDetector(config)

isTimeSet = False


# Handle HTTP requests.
class CamHandler(BaseHTTPRequestHandler):
    # Options
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        print("Sent options.")

    def do_GET(self):
        print(self.path)
        # Serve root website
        if self.path == '/':
            with open('index.html', 'rb') as file:
                print("Served website.")
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())

        # Serve web files
        elif self.path.endswith('.js') or self.path.endswith('.css') or self.path.endswith('.html'):
            with open(self.path[1:], 'rb') as file:
                print("Served file " + self.path[1:])

                self.send_response(200)
                if self.path.endswith('.js'):
                    self.send_header('Content-type', 'text/javascript')
                elif self.path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif self.path.endswith('.html'):
                    self.send_header('Content-type', 'text/html')

                self.end_headers()
                self.wfile.write(file.read())

        # Serve camera stream
        elif self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            print("Serving mjpg...")
            while True:
                    try:
                        img = changeDetectorInstance.get_current_image()
                        r, buf = cv2.imencode(".jpg", img)
                        self.wfile.write(b'--jpgboundary\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', str(len(buf)))
                        self.end_headers()
                        self.wfile.write(bytearray(buf))
                        self.wfile.write(b'\r\n')
                    except KeyboardInterrupt:
                        break
            return

        # Camera control request - Less sensitivity
        elif self.path.endswith('less'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            changeDetectorInstance.minWidth = config["less_sensitivity"]
            changeDetectorInstance.minHeight = config["less_sensitivity"]
            print("Changed sensitivity to less")
            return

        # Camera control request - More sensitivity
        elif self.path.endswith('more'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            changeDetectorInstance.minWidth = config["more_sensitivity"]
            changeDetectorInstance.minHeight = config["more_sensitivity"]
            print("Changed sensitivity to more")
            return

        # Camera control request - Default sensitivity
        elif self.path.endswith('default'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            changeDetectorInstance.minWidth = config["min_width"]
            changeDetectorInstance.minHeight = config["min_width"]
            print("Changed sensitivity to default")
            return

        # Camera control request - Start recording
        elif self.path.endswith('start'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            changeDetectorInstance.arm()
            print("Started recording.")
            return

        # Camera control request - Stop recording
        elif self.path.endswith('stop'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            changeDetectorInstance.disarm()
            print("Stopped recording.")
            return

        # Camera control request - Delete all photos
        elif self.path.endswith('delete-final'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'success')
            os.system('rm /var/www/html/photos/*')
            print("Deleted photos.")
            return

        # Camera control request - Get camera status
        elif self.path.endswith('get-status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            sensitivity = "unknown"
            if changeDetectorInstance.minWidth == config["less_sensitivity"]:
                sensitivity = "less"
            elif changeDetectorInstance.minWidth == config["min_width"]:
                sensitivity = "default"
            elif changeDetectorInstance.minWidth == config["more_sensitivity"]:
                sensitivity = "more"
            send_data = {
                "mode": changeDetectorInstance.mode,
                "sensitivity": sensitivity
            }
            json_data = json.dumps(send_data)
            self.wfile.write(json_data.encode("utf-8"))
            print("Returned camera status.")
            return

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Page not found')
            print("Page not found.")

    # POST request for updating time
    def do_POST(self):
        print(self.path)
        if self.path.endswith('set-time'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data_string.decode('utf-8'))

            print("Time: " + data["timeString"])

            global isTimeSet
            if isTimeSet is True:
                print("Time has already been set during this powerup.")
            else:
                os.system('date -s "' + data["timeString"] + '"')
                isTimeSet = True
                print("Time updated.")

            self.wfile.write(b'success')



# Threaded server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""


def main():
    try:
        changeDetectorInstance.start()
        server = ThreadedHTTPServer(('', 9090), CamHandler)
        print("server started")
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        changeDetectorInstance.cancel()
        server.socket.close()


if __name__ == '__main__':
    main()
