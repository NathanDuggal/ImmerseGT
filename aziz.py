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

import matplotlib
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from PIL import Image


MIN_AREA = 20
DISPLAY_STREAM = False

# setup plots
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
ax.axes.set_xlim(0,1000)
ax.axes.set_ylim(0,1000)
line1, = ax.plot([], []) # Returns a tuple of line objects, thus the comma


#start stream
vid = cv2.VideoCapture(0)

# setup aruco tags
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()
green_range = [np.array([40,50,50]), np.array([70,255,255])]




class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.health = 100
        self.ammo = 50
        self.connected = False

    def get_player_stats(self):
        return "Player :"
    

players = {1: Player('Bob'), 
            2: Player('Joe'), 
            3: Player('Bill')}




def dist(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


def get_contours(mask, min_area):
    mask = cv2.inRange(img_hsv, green_range[0], green_range[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    x, y = [], []
    for c in contours:
        if cv2.contourArea(c) > 20:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            x.append(cX)
            y.append(cY)
    return x, y


def get_people_vectors(aruco_x, aruco_y, green_x, green_y, ids):
    green_point_ownership = {e:[] for e in zip(aruco_x,aruco_y)}
    for i in range(len(green_x)):
        gx = green_x[i]
        gy = green_y[i]
        distances = []
        for j in green_point_ownership:
            rx = j[0]
            ry = j[1]
            dist_between = dist(gx,gy,rx,ry)
            if dist_between < 200:
                distances.append((dist(gx,gy,rx,ry),j))
        if distances != []:
            green_point_ownership[min(distances, key= lambda x: x[0])[1]].append((gx,gy))

    people_vectors = []
    for person in green_point_ownership:
        if green_point_ownership[person]:
            point_list = ([x[0] for x in green_point_ownership[person]], [x[1] for x in green_point_ownership[person]])
            xs = sum(point_list[0]) / float(len(point_list[0]))
            ys = sum(point_list[1]) / float(len(point_list[1]))
            people_vectors.append(((person[0],person[1]),(xs,ys)))

    return {ids[list(zip(aruco_x,aruco_y)).index(vector[0])][0] : vector for vector in people_vectors}


while True:
    ret, frame = vid.read()
    ax.cla()

    # checks if frame is actually read
    if (not isinstance(frame, type(None))):
        img_hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # mask image, get contours
        mask = cv2.inRange(img_hsv, green_range[0], green_range[1])
        green_x, green_y = get_contours(mask, MIN_AREA)

        # remove contours for display
        output_hsv = 0
        if DISPLAY_STREAM:
            output_hsv = img_hsv.copy()
            output_hsv[np.where(mask==0)] = 0
        
        # get x and y coordinates of aruco tags
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
        aruco_x = [n[0][0][0] for n in corners]
        aruco_y = [n[0][0][1] for n in corners]

        # get vectors for ids that have green {id: [[x1,y1],[x2,y2]]}
        people_vectors = get_people_vectors(aruco_x, aruco_y, green_x, green_y, ids)

        ax.clear()

        for person in people_vectors:
            ax.plot([people_vectors[person][0][0],people_vectors[person][1][0]],
                    [people_vectors[person][0][1],people_vectors[person][1][1]])
            
        ax.scatter([0,1920], [0,1080])
        ax.scatter(aruco_x,aruco_y,c='r')
        ax.scatter(green_x,green_y,c='g')


        plt.pause(0.02)
        #graph_image = cv2.cvtColor(np.array(fig.canvas.get_renderer()._renderer),cv2.COLOR_RGB2BGR) 
        plt.show()

        if DISPLAY_STREAM:
            cv2.imshow("img", cv2.cvtColor(output_hsv, cv2.COLOR_HSV2BGR))

        # the 'q' button is set as the quitting button you may use any
        if cv2.waitKey(205) & 0xFF == ord('q'):
            break
        
# After the loop release the cap object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()