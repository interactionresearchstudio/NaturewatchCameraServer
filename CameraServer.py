import json
import cv2
import numpy as np
from imutils.video.pivideostream import PiVideoStream
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time

config = json.load(open("config.json"))

# Open video stream from Pi camera.
vs = PiVideoStream().start()
time.sleep(2.0)

# NatureCam implementation
class NatureCam(Thread):
    minWidth = config["min_width"]
    maxWidth = config["max_width"]
    minHeight = config["min_height"]
    maxHeight = config["max_height"]

    mode = 0
    avg = None
    lastPhotoTime = 0
    numOfPhotos = 0

    activeColour = (255,255,0)
    inactiveColour = (100,100,100)
    isMinActive = False

    currentImage = None

    def __init__(self):
        super(NatureCam, self).__init__()
        self.daemon = True
        self.cancelled = False

    def run(self):
        while not self.cancelled:
            self.update()

    def cancel(self):
        self.cancelled = True

    def takePhoto(image):
        timestamp = datetime.datetime.now()
        filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + ".jpg"
        cv2.imwrite(filename, image)

    def rotateImage(img):
        (h,w) = img.shape[:2]
        center = (w/2, h/2)
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        return cv2.warpAffine(img, M, (w,h))

    def detectChangeContours(img):
        global avg
        global lastPhotoTime
        global numOfPhotos

        # convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if avg is None:
            avg = gray.copy().astype("float")
            # remember to truncate capture for Pi
            rawCapture.truncate(0)
            if config["rotate_display"] == 1:
                return rotateImage(img)
            else:
                return img

        # add to accumulation model and find the change
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        # threshold, dilate and find contours
        thresh = cv2.threshold(frameDelta, config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour
        largestContour = getLargestContour(cnts)

        if largestContour is None:
            if config["rotate_display"] == 1:
                return rotateImage(img)
            else:
                return img

        (x, y, w, h) = cv2.boundingRect(largestContour)

        # if the contour is too small, just return the image.
        if w > maxWidth or w < minWidth or h > maxHeight or h < minHeight:
            if config["rotate_display"] == 1:
                return rotateImage(img)
            else:
                return img

        # otherwise, draw the rectangle
        if time.time() - lastPhotoTime > config['min_photo_interval_s']:
            if config["rotate_saved"] == 1:
                takePhoto(rotateImage(img))
            else:
                takePhoto(img)
            numOfPhotos = numOfPhotos + 1
            lastPhotoTime = time.time()

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)

        if config["rotate_display"] == 1:
            img = rotateImage(img)

        cv2.putText(img, "%d" % numOfPhotos, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

        return img

    def getLargestContour(contours):
        if not contours:
            return None
        else:
            areas = [cv2.contourArea(c) for c in contours]
            maxIndex = np.argmax(areas)
            return contours[maxIndex]

    def displayMinMax(img):
        if isMinActive is True:
            minColour = activeColour
            maxColour = inactiveColour
        else:
            minColour = inactiveColour
            maxColour = activeColour

        cv2.rectangle(img, (320/2-minWidth/2,240/2-minHeight/2), (320/2+minWidth/2,240/2+minHeight/2), minColour, 2)
        cv2.rectangle(img, (320/2-maxWidth/2,240/2-maxHeight/2), (320/2+maxWidth/2,240/2+maxHeight/2), maxColour, 2)
        if config["rotate_display"] == 1:
            return rotateImage(img)
        else:
            return img

    def increaseMinMax(increment):
        global minWidth
        global minHeight
        global maxWidth
        global maxHeight

        if isMinActive is True:
            minWidth = minWidth + increment
            minHeight = minHeight + increment
            if minWidth > maxWidth:
                minWidth = maxWidth
                minHeight = maxHeight
        else:
            maxWidth = maxWidth + increment
            maxHeight = maxHeight + increment
            if maxWidth > 320:
                maxWidth = 320
                maxHeight = 320
            if maxHeight >= 240:
                maxHeight = 240

    def decreaseMinMax(increment):
        global minWidth
        global minHeight
        global maxWidth
        global maxHeight

        if isMinActive is True:
            minWidth = minWidth - increment
            minHeight = minHeight - increment
            if minWidth < 0:
                minWidth = 0
                minHeight = 0
        else:
            maxWidth = maxWidth - increment
            maxHeight = maxHeight - increment
            if maxWidth < minWidth:
                maxWidth = minWidth
                maxHeight = minHeight
            if maxWidth < 240:
                maxHeight = maxWidth
            elif maxWidth >= 240:
                maxHeight = 240

    def arm(self):
        global mode
        mode = 1

    def disarm(self):
        global mode
        mode = 0

    def update(self):
        global currentImage
        currentImage = vs.read()

        if mode == 0:
            currentImage = displayMinMax(currentImage)
        elif mode == 1:
            currentImage = detectChangeContours(currentImage)

    def getCurrentImage(self):
        return currentImage

natureCamInstance = NatureCam()
natureCamInstance.start()

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

# Threaded server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""

def main():
    try:
        server = ThreadedHTTPServer(('', 9090), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        vs.stop()
        server.socket.close()


if __name__ == '__main__':
    main()
