import cv2
from imutils.video.pivideostream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import time

vs = PiVideoStream().start()
time.sleep(2.0)

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print self.path
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			print("Serving mjpg...")
            while True:
                img = vs.read()
                r, buf = cv2.imencode(".jpg",img)
				self.wfile.write("--jpgboundary\r\n")
				self.send_header('Content-type','image/jpeg')
				self.send_header('Content-length',str(len(buf)))
				self.end_headers()
				self.wfile.write(bytearray(buf))
				self.wfile.write('\r\n')

		if self.path.endswith('.html') or self.path=="/":
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<img src="http://naturewatch-cam.local:9090/cam.mjpg"/>')
			self.wfile.write('</body></html>')
			return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate thread"""

def main():
	try:
		server = ThreadedHTTPServer(('',9090),CamHandler)
		print "server started"
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()

if __name__ == '__main__':
	main()

vs.stop()
