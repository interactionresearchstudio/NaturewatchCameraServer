# NaturewatchCameraServer

This is a Python server script that captures a video stream from a Pi Camera and serves it as a .mjpg through a control website to another device. Part of the My Naturewatch project in collaboration with the RCA.

## Requirements

- OpenCV 3.1.0, along with OpenCV_Contrib modules. 
- Python 3.4+
- Raspbian Stretch
- Picamera Python module 
- Raspberry Pi Zero W or 3 (built-in WiFi)
- 16GB+ SD card

## Running the main script

Simply run the script with Python (as super user, so that the server can run on port 80). 

	sudo python3 CameraServer.py 80
	
You can then access the camera controls at

	http://localhost.local/
	
Be sure to replace `localhost.local` with whatever hostname the Pi has.

## Reporting bugs

Please provide as much information as possible. If you'd like to open an issue about a 
possible bug, please do so here and include as much information as possible. 

## Pull requests

If you'd like to submit a pull request, please let us know whether you're submitting a
new feature, or a bug fix. We have an internal release schedule, so please don't be
offended if it takes us some time to fit your PR in! We will respond to every single 
one of them and let you know if we're evaluating it for a full release. It's also worth 
testing your PR against the `dev` branch, which has more experimental features.

## Support

If you require support, please head over to the [My Naturewatch Forum](https://mynaturewatch.net/forum).

