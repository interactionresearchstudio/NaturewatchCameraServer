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

        if self.path.endswith('.html') or self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="http://naturewatch-cam.local:9090/cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return

        if self.path.endswith('changeActiveSquare'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.isMinActive = not changeDetectorInstance.isMinActive
            return

        if self.path.endswith('increaseMinMax'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.increaseMinMax(5)
            return

        if self.path.endswith('decreaseMinMax'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            changeDetectorInstance.decreaseMinMax(5)
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
        vs.stop()
        server.socket.close()


if __name__ == '__main__':
    main()
