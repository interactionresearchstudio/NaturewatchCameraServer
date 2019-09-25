# NaturewatchCameraServer

This is a Python server script that captures a video stream from a Pi Camera and serves it as a .mjpg through a control website to another device. Part of the My Naturewatch project in collaboration with the RCA.


## Enable SSH (to be automated) 

Add a blank file named `ssh` to the boot folder on the SD card

## Set up OTG ethernet (to be automated) 

Follow the guide created by gbaman to set up OTG ethernet over USB serial https://gist.github.com/gbaman/975e2db164b3ca2b51ae11e45e8fd40a

## Requirements

- Docker installed on Raspbian Stretch
https://gist.github.com/mikevanis/e360f45e394674b59d663fdf0470d42f

## Running the server

Build the docker container
	
	docker-compose build
	
## Configuring the wifi setup

Run the config setup python script. This will reboot the pi
	
	sudo python3 NaturewatchCameraServer/cfgsetup.py

## Access the interface
    
The website is then accessible through its hostname:

	http://raspberrypi.local/
	
Be sure to replace `raspberrypi.local` with whatever hostname the Pi has.

## Running tests

You can run tests directly on the Raspberry pi to test the various functions of the
software as well as the API. After building the container, run the tests with pytest.

    docker run \
    --device /dev/vcsm --device /dev/vchiq \
    -p 5000:5000 \
    -v ~/data:/naturewatch_camera_server/static/data \
    naturewatchcameraserver \
    pytest -v naturewatch_camera_server/

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

