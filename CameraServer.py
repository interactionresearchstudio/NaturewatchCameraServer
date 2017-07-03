#!/usr/bin/env python
import json
import cv2
import os
import numpy as np
import imutils
from imutils.video.pivideostream import PiVideoStream
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time
import datetime

os.chdir("/home/pi/CameraServer")
config = json.load(open("config.json"))
os.chdir("/var/www/html/photos")

# Open video stream from Pi camera.
vs = PiVideoStream().start()
time.sleep(2.0)

# NatureCam implementation
class NatureCam(Thread):

    def __init__(self):
        super(NatureCam, self).__init__()
        self.daemon = True
        self.cancelled = False
        self.minWidth = config["min_width"]
        self.maxWidth = config["max_width"]
        self.minHeight = config["min_height"]
        self.maxHeight = config["max_height"]

        self.mode = 0
        self.avg = None
        self.lastPhotoTime = 0
        self.numOfPhotos = 0

        self.activeColour = (255,255,0)
        self.inactiveColour = (100,100,100)
        self.isMinActive = False
        self.currentImage = None

    def run(self):
        while not self.cancelled:
            self.update()

    def cancel(self):
        self.cancelled = True

    def takePhoto(self, image):
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"
        cv2.imwrite(filename, image)

    def rotateImage(self, img):
        (h,w) = img.shape[:2]
        center = (w/2, h/2)
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        return cv2.warpAffine(img, M, (w,h))

    def detectChangeContours(self, img):
        # convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if self.avg is None:
            self.avg = gray.copy().astype("float")
            return img

        # add to accumulation model and find the change
        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold, dilate and find contours
        thresh = cv2.threshold(frameDelta, config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        largestContour = self.getLargestContour(cnts)

        if largestContour is None:
            return img

        (x, y, w, h) = cv2.boundingRect(largestContour)

        # if the contour is too small, just return the image.
        if w > self.maxWidth or w < self.minWidth or h > self.maxHeight or h < self.minHeight:
            return img

        # otherwise, draw the rectangle
        if time.time() - self.lastPhotoTime > config['min_photo_interval_s']:
            self.takePhoto(img)
            self.numOfPhotos = self.numOfPhotos + 1
            self.lastPhotoTime = time.time()

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(img, "%d" % self.numOfPhotos, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

        return img

    def getLargestContour(self, contours):
        if not contours:
            return None
        else:
            areas = [cv2.contourArea(c) for c in contours]
            maxIndex = np.argmax(areas)
            return contours[maxIndex]

    def displayMinMax(self, img):
        if self.isMinActive is True:
            minColour = self.activeColour
            maxColour = self.inactiveColour
        else:
            minColour = self.inactiveColour
            maxColour = self.activeColour

        cv2.rectangle(img, (320/2-self.minWidth/2,240/2-self.minHeight/2), (320/2+self.minWidth/2,240/2+self.minHeight/2), minColour, 2)
        cv2.rectangle(img, (320/2-self.maxWidth/2,240/2-self.maxHeight/2), (320/2+self.maxWidth/2,240/2+self.maxHeight/2), maxColour, 2)
        return img

    def increaseMinMax(self, increment):
        if self.isMinActive is True:
            self.minWidth = self.minWidth + increment
            self.minHeight = self.minHeight + increment
            if self.minWidth > self.maxWidth:
                self.minWidth = self.maxWidth
                self.minHeight = self.maxHeight
        else:
            self.maxWidth = self.maxWidth + increment
            self.maxHeight = self.maxHeight + increment
            if self.maxWidth > 320:
                self.maxWidth = 320
                self.maxHeight = 320
            if self.maxHeight >= 240:
                self.maxHeight = 240

    def decreaseMinMax(self, increment):
        if self.isMinActive is True:
            self.minWidth = self.minWidth - increment
            self.minHeight = self.minHeight - increment
            if self.minWidth < 0:
                self.minWidth = 0
                self.minHeight = 0
        else:
            self.maxWidth = self.maxWidth - increment
            self.maxHeight = self.maxHeight - increment
            if self.maxWidth < self.minWidth:
                self.maxWidth = self.minWidth
                self.maxHeight = self.minHeight
            if self.maxWidth < 240:
                self.maxHeight = self.maxWidth
            elif self.maxWidth >= 240:
                self.maxHeight = 240

    def arm(self):
        self.mode = 1

    def disarm(self):
        self.mode = 0

    def update(self):
        self.currentImage = vs.read()

        if self.mode == 0:
            self.currentImage = self.displayMinMax(self.currentImage)
        elif self.mode == 1:
            self.currentImage = self.detectChangeContours(self.currentImage)

    def getCurrentImage(self):
        return self.currentImage


natureCamInstance = NatureCam()

# Handle HTTP requests.
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print self.path
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            print("Serving mjpg...")
            while True:
                img = natureCamInstance.getCurrentImage()
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
            natureCamInstance.isMinActive = not natureCamInstance.isMinActive
            return

        if self.path.endswith('increaseMinMax'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            natureCamInstance.increaseMinMax(5)
            return

        if self.path.endswith('decreaseMinMax'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            natureCamInstance.decreaseMinMax(5)
            return

        if self.path.endswith('start'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            natureCamInstance.arm()
            return

        if self.path.endswith('stop'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('success')
            natureCamInstance.disarm()
            return

# Threaded server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""

def main():
    try:
        natureCamInstance.start()
        server = ThreadedHTTPServer(('', 9090), CamHandler)
        print "server started"
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        natureCamInstance.cancel()
        vs.stop()
        server.socket.close()


if __name__ == '__main__':
    main()
