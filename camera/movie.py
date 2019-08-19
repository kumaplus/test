#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import picamera
import time
import sys

FILEPATH = '/home/pi/raspi2-sample/camera/data/'
MOVIE_INTERVAL = 600

def main(now):
    filename = FILEPATH + now + ".h264"
    with picamera.PiCamera() as camera:
        camera.hflip = True
        camera.vflip = True
        camera.resolution = (1024,768)
        camera.brightness = 70
        camera.start_recording(filename)
        time.sleep(MOVIE_INTERVAL)
        camera.stop_recording()

if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        print("Invalid argument.")
        sys.exit(1)
    main(sys.argv[1])
