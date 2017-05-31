# CameraServer

This is a Python server script that captures a video stream from a Pi Camera and serves it an an mjpg through a website to another device. Part of the Citizen Naturewatch project in collaboration with the RCA.

## Requirements

- OpenCV 3.1.0, along with OpenCV_Contrib modules. 
- Python 2.7
- Picamera array module
- Raspberry Pi 3
- 16GB SD card

## Running the main script

Simply run the script with Python. 

	python CameraServer.py
	
You can then access the OpenCV stream at

	localhost.local:9090/index.mjpg
	
Be sure to replace `localhost.local` with whatever hostname the Pi has.

## ToDo
