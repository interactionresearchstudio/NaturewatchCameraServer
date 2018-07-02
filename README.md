# CameraServer

This is a Python server script that captures a video stream from a Pi Camera and serves it an an mjpg through a website to another device. Part of the Citizen Naturewatch project in collaboration with the RCA.

## Requirements

- OpenCV 3.1.0, along with OpenCV_Contrib modules. 
- Python 3.4+
- Picamera 
- Raspberry Pi Zero W or 3 (built-in WiFi)
- 16GB+ SD card

## Running the main script

Simply run the script with Python (as super user, so that the server can run on port 80). 

	sudo python3 CameraServer.py
	
You can then access the camera controls at

	http://localhost.local/
	
Be sure to replace `localhost.local` with whatever hostname the Pi has.

## Reporting bugs

Please provide as much information as possible. If you'd like to open an issue about a 
possible bug, please do so here and include as much information as possible. 

## Support

If you require support, please head over to the [My Naturewatch Forum](https://mynaturewatch.net/forum).

