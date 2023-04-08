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
import requests

import matplotlib
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from PIL import Image
import json


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


class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Player:
    def __init__(self, id, name, color):
        self.id = id
        self.color = color
        self.xPos = 0
        self.yPos = 0
        self.xDir = 0
        self.yDir = 0
        self.kills = 0
        self.name = name
        self.score = 0
        self.deaths = 0
        self.health = 100
        self.dead = False
        self.ammo = 10
        self.bulletDamage = 10
        self.connected = False
        self.in_base = False
        self.was_green = False
        self.is_green = False
        self.player_radius = 20

    def get_player_stats(self):
        return f"Player: id: {str(self.id)} , green: {self.is_green}, connnected: {self.connected}, health: {self.health}"

    def gets_shot(self, shooter):
        # Extracting the components of the ray
        start_x, start_y = shooter.xPos, shooter.yPos
        end_x, end_y = shooter.xDir, shooter.yDir
        
        # Finding the direction vector of the ray
        direction_x = end_x - start_x
        direction_y = end_y - start_y
        
        # Finding the vector from the ray's start point to the player's center
        player_to_ray_start_x = start_x - self.xPos
        player_to_ray_start_y = start_y - self.yPos
        
        # Calculating the coefficients of the quadratic equation for intersection
        a = direction_x**2 + direction_y**2
        b = 2 * (player_to_ray_start_x * direction_x + player_to_ray_start_y * direction_y)
        c = player_to_ray_start_x**2 + player_to_ray_start_y**2 - self.player_radius**2
        
        # Calculating the discriminant
        discriminant = b**2 - 4 * a * c
        
        # Checking if the ray intersects the player
        if discriminant >= 0 and shooter.was_green == False:
            # If the discriminant is non-negative, the ray intersects the player
            self.health -= shooter.bulletDamage
            if self.health <= 0:
                self.dead = True
            return True
        else:
            return False

    


players = {1: Player(1, "Bradley", "Red"), 
            2: Player(2, 'Joe Biden', "Red"), 
            3: Player(3, 'Bill Clinton', "Red"),
            4: Player(4, "Mary's Lamb", "Blue"), 
            5: Player(5, 'Kot', "Blue"), 
            6: Player(6, 'Jill Biden', "Blue")}


#made by chatgpt
def check_ray_intersection(player, shooter):
    # Extracting the components of the ray
    start_x, start_y = shooter.xPos, shooter.yPos
    end_x, end_y = shooter.xDir, shooter.yDir
    
    # Finding the direction vector of the ray
    direction_x = end_x - start_x
    direction_y = end_y - start_y
    
    # Finding the vector from the ray's start point to the player's center
    player_to_ray_start_x = start_x - player.xPos
    player_to_ray_start_y = start_y - player.yPos
    
    # Calculating the coefficients of the quadratic equation for intersection
    a = direction_x**2 + direction_y**2
    b = 2 * (player_to_ray_start_x * direction_x + player_to_ray_start_y * direction_y)
    c = player_to_ray_start_x**2 + player_to_ray_start_y**2 - player.player_radius**2
    
    # Calculating the discriminant
    discriminant = b**2 - 4 * a * c
    
    # Checking if the ray intersects the player
    if discriminant >= 0:
        # If the discriminant is non-negative, the ray intersects the player
        return True
    else:
        # If the discriminant is negative, the ray does not intersect the player
        return False

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


def update_player_vectors(aruco_x, aruco_y, green_x, green_y, ids, players):
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

    vectors = {ids[list(zip(aruco_x,aruco_y)).index(vector[0])][0] : vector for vector in people_vectors}

    for player in players:
        players[player].connected = False
    
    if aruco_x:
        for id,i in zip(ids,list(range(0,len(aruco_x)))):
            id = id[0]
            print(id,i)
            players[id].xPos = aruco_x[i]
            players[id].yPos = aruco_y[i]
            players[id].was_green = players[id].is_green
            players[id].is_green = False
            players[id].connected = True

        for player_id in vectors:
            players[player_id].is_green = True
            players[player_id].xDir = vectors[player_id][1][0]
            players[player_id].yDir = vectors[player_id][1][1]

    return vectors


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
        (corners_, ids_, rejected_) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
        # corners, ids, rejected = [],[],[]
        corners, ids, rejected = corners_, ids_, rejected_
        # for c,id in enumerate(ids):
        #     print(c)
        #     if id in [1,2,3,4,5,6]:
        #         corners.append(corners_[c])
        #         ids.append(ids_[c])
        #         rejected.append(rejected_[c])
        #     else:
        #         print(id)


        aruco_x = [n[0][0][0] for n in corners]
        aruco_y = [n[0][0][1] for n in corners]

        # get vectors for ids that have green {id: [[x1,y1],[x2,y2]]} and updates player movements
        people_vectors = update_player_vectors(aruco_x, aruco_y, green_x, green_y, ids, players)


        #updates each from per player like shooting
        for player in players:
            if players[player].is_green and not players[player].was_green and players[player].ammo > 0 and not players[player].dead:
                shooter = players[player]
                shooter.ammo -= 1
                for victim in players:
                    if victim != player:
                        if players[victim].gets_shot(shooter):
                            shooter.kills+=1
            print(players[player].get_player_stats())

        if int(time.time()) % 3 == 0:
            new_json = {}
            for id in players:
                new_json[id] = {"Name": players[id].name,"Health": players[id].health, "Score": players[id].score, "Kills": players[id].kills, "Deaths": players[id].deaths, "Ammo": players[id].ammo, "Connected": players[id].connected}
            requests.post('http://127.0.0.1:5000/hello', json=json.dumps(new_json))

        # plotting
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