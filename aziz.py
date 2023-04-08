import cv2
import numpy as np
from tkinter import Tk, filedialog
import os
import math
import time
from multiprocessing import Process, Value, Array
from flask import Flask
from flask import render_template
from flask import send_from_directory
import matplotlib.pyplot as plt
import matplotlib
from flask import Flask, request, jsonify
from PIL import Image

vid = cv2.VideoCapture(0)


arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()
green_range = [np.array([40,0,0]), np.array([70,255,255])]




while True:
    ret, frame = vid.read()

    # checks if frame is actually read
    if (not isinstance(frame, type(None))):
        img_hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # lower mask (0-10)
        mask = cv2.inRange(img_hsv, green_range[0], green_range[1])

        output_hsv = img_hsv.copy()
        output_hsv[np.where(mask==0)] = 0

        cv2.imshow('frame', cv2.cvtColor(output_hsv, cv2.COLOR_HSV2BGR))

        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)

        print(ids)

        # the 'q' button is set as the quitting button you may use any
        if cv2.waitKey(205) & 0xFF == ord('q'):
            break
        
# After the loop release the cap object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()