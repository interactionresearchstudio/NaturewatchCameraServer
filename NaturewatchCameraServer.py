#!/usr/bin/env python
import json
import cv2
import os
import imutils
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from ChangeDetector import ChangeDetector

os.chdir("/home/pi/NaturewatchCameraServer")
config = json.load(open("config.json"))
os.chdir("/var/www/html/photos")

# NatureCam implementation
changeDetectorInstance = ChangeDetector(config)

isTimeSet = False

# Handle HTTP requests.
class CamHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.close()

    def do_GET(self):
        print(self.path)
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            print("Serving mjpg...")
            while True:
                img = changeDetectorInstance.get_current_image()
                r, buf = cv2.imencode(".jpg", img)
                self.wfile.write("--jpgboundary\r\n")
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length', str(len(buf)))
                self.end_headers()
                self.wfile.write(bytearray(buf))
                self.wfile.write('\r\n')

        if self.path.endswith('less'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            changeDetectorInstance.minWidth = config["less_sensitivity"]
            changeDetectorInstance.minHeight = config["less_sensitivity"]
            return

        if self.path.endswith('more'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            changeDetectorInstance.minWidth = config["more_sensitivity"]
            changeDetectorInstance.minHeight = config["more_sensitivity"]
            return

        if self.path.endswith('default'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            changeDetectorInstance.minWidth = config["min_width"]
            changeDetectorInstance.minHeight = config["min_width"]
            return

        if self.path.endswith('start'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            changeDetectorInstance.arm()
            return

        if self.path.endswith('stop'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            changeDetectorInstance.disarm()
            return

        if self.path.endswith('delete-final'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            self.wfile.close()
            os.system('rm /var/www/html/photos/*')
            return

        if self.path.endswith('get-status'):
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
            self.wfile.write(json_data)
            self.wfile.close()
            return

        if self.path.endswith('info'):
            send_data = {
                "temp": self.get_cpu_temperature(),
            }
            json_data = json.dumps(send_data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_data)
            self.wfile.close()
            return

    def do_POST(self):
        print(self.path)
        if self.path.endswith('set-time'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data_string)

            print("Time: " + data["timeString"])

            global isTimeSet
            if isTimeSet is True:
                print("Time has already been set during this powerup.")
            else:
                os.system('date -s "' + data["timeString"] + '"')
                isTimeSet = True
                print("Time updated.")

            self.wfile.write('success')

    @staticmethod
    def get_cpu_temperature():
        res = os.popen('vcgencmd measure_temp').readline()
        return res.replace("temp=", "").replace("'C\n", "")


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
