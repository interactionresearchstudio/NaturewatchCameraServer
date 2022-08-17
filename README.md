![Build Image](https://github.com/interactionresearchstudio/NaturewatchCameraServer/workflows/Build%20Image/badge.svg)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/interactionresearchstudio/NaturewatchCameraServer)
![GitHub all releases](https://img.shields.io/github/downloads/interactionresearchstudio/NaturewatchCameraServer/total)

# NaturewatchCameraServer

This is the main software for the My Naturewatch Camera. It is a Python server 
script that captures a video stream from a Pi Camera and serves it as a .mjpg 
through a control website to another device. The website can be used to start 
a photo capture or video capture based on motion detected in the frame. The 
software is designed to run on a Raspberry Pi Zero W so that you can make your 
own low-cost wildlife camera.

Part of the My Naturewatch project by the Interaction Research Studio, in collaboration with the RCA.

# How to install

To use the image, download the lastest zip build from [Releases](https://github.com/interactionresearchstudio/NaturewatchCameraServer/releases)

Uncompress and burn this to an SD card. We recommend using [Balena Etcher](https://www.balena.io/etcher/) for this.

## Configuring the wifi setup

The device automatically creates a hotspot network named MyNatureWatch-12345, with the numbers being a unique ID. 

You can also connect the device directly to a home network by following this [guide](https://mynaturewatch.net/instructions-homenetwork)

## Access the interface

The website is then accessible through its IP address:

	http://192.168.50.1
	
If your device has Bonjour installed, you can also use:

	http://mynaturewatchcamera.local/
	

## Reporting bugs

Please provide as much information as possible. If you'd like to open an issue about a
possible bug, please do so here and include as much information as possible. You can 
also open an issue if you would like to request a new feature. 

## Pull requests

If you'd like to submit a pull request, please let us know whether you're submitting a
new feature, or a bug fix. Make sure to do a self review, and test on at least one type 
of Raspberry Pi. Please don't be offended if it takes us some time to fit your PR in! 
We will respond to every single one of them and let you know if we're evaluating it for 
a full release.

## Support

If you require support, please head over to the [My Naturewatch Forum](https://mynaturewatch.net/forum).

