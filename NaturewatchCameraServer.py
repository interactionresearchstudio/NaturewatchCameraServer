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


# Handle HTTP requests.
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            print("Serving mjpg...")
            while True:
                img = changeDetectorInstance.getCurrentImage()
                img = imutils.rotate(img, angle=180)
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
            changeDetectorInstance.minWidth = config["less_sensitivity"]
            changeDetectorInstance.minHeight = config["less_sensitivity"]
            return

        if self.path.endswith('more'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.minWidth = config["more_sensitivity"]
            changeDetectorInstance.minHeight = config["more_sensitivity"]
            return

        if self.path.endswith('default'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.minWidth = config["min_width"]
            changeDetectorInstance.minHeight = config["min_width"]
            return

        if self.path.endswith('start'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.arm()
            return

        if self.path.endswith('stop'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.disarm()
            return

        if self.path.endswith('delete-final'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            os.system('rm /var/www/html/photos/*')
            return



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
        #vs.stop()
        server.socket.close()


if __name__ == '__main__':
    main()
