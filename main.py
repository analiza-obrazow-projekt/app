import asyncio
import os
import cv2
import json
import js
import numpy as np
import pyscript
from pyscript import display
from pyodide.http import pyfetch
from js import document
import matplotlib.pyplot as plt
import math
from matplotlib import pyplot
import random
import pyodide
import pandas as pd



# pyodide.register_js_function(load_image)
#liczba mrówek szukających celu (nie przesadzać za względu na ograniczenia pamięci każda to jedna tablica 512x512 booli)
antNumber=125

#punkt z którego mrówki zaczynają (jeśli na polu czarnym mrówki pozostaną w miejscu)
start= np.loadtxt("start.csv", delimiter=",", dtype='i').tolist()

#punkt docelowy
goal = np.loadtxt("goal.csv", delimiter=",", dtype='i').tolist()
# start= [200, 404]
# goal = [62,504]
# start= [62,504]
# goal = [443,56]

#prędkość poruszania (różnica w pikselach)
speed=4

#obraz - nazwa pliku
imageName="test2.jpg"

#rozmiar obrazu powyżej (nie dawać więcej niż 512 bo nie testowane)
textureSize=512

def calculate_shortest_path():
    img = convert_to_binary_array(imageName)
    tmp=np.transpose(img)
    if check_points(img,start,goal):
        ants=[Ant(start[0],start[1]) for i in range(antNumber)]
        tmp=round(textureSize*math.sqrt(2))
        pheromones = [[tmp-round(math.sqrt(math.pow(i-goal[0],2)+math.pow(j-goal[1],2))) for j in range(textureSize)] for i in range(textureSize)]
        while (Ant.desiredPathNumber>0):
            for i in range(len(ants)):
                ants[i].move(pheromones, img)
        d = np.zeros((512,512), np.uint8)
        for j in range(512):
            d=[1 for i in Ant.paths[0][j] if i]   
        
        # wczytanie mapy
        road_map = cv2.imread(imageName, cv2.COLOR_BGR2GRAY)

        # # binaryzacja mapy
        _, road_map_bin = cv2.threshold( road_map, 126, 255, cv2.THRESH_BINARY )

        # wczytanie współrzędnych wskazujących punkty trasy
        loaded_input = d
        all_road_coordinates = []
        NX, NY = loaded_input.shape
        for x in range(NX):
            for y in range(NY):
                if loaded_input[x,y] == True:
                    all_road_coordinates.append([x,y])

        # output w takiej samej formie, co input, ale z wartościami będącymi szerokością trasy
        output = np.zeros((512,512), np.uint8)
        for coordinates in all_road_coordinates:
            X, Y = coordinates
            output[X,Y] = getRoadWidth(road_map_bin,coordinates)     
        show_result_image(output)
    else:
        display("Wybrane punkty nie znajdują się na ścieżce", target="result")  

def show_input_image():
    fig, ax = plt.subplots()
    image = cv2.imread(imageName)
    ax.imshow(image)
    ax.invert_yaxis()
    display(fig, target="input")

def show_points():
    display("start:", target="points")
    display(start, target="points")
    display("goal:", target="points")
    display(goal, target="points")
    
def check_points(img, start, goal):
    try:
        startOK = (img[start[0]][start[1]]==255)
        goalOK = (img[goal[0]][goal[1]]==255)
        return (startOK and goalOK)
    except IndexError as e:
        return False


def show_result_image(output):
    fig, ax = plt.subplots()
    plt.imshow(output)
    display(fig, target="result")

def bgr2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    thresh, im_bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return im_bw

def convert_to_binary_array(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    kernel = np.ones((5,5),np.uint8)
    img = cv2.dilate(img,kernel,iterations = 1)
    thresh, im_bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return im_bw

class Ant:
    #liczba dróg które mają zostać znalezione
    desiredPathNumber=10
    
    #tablica na sciezki
    paths=[]
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.trail=[[False for i in range(textureSize)] for j in range(textureSize)]
        self.px=x
        self.py=y

    def reach(self, p):
        for i in range(textureSize):
            for j in range(textureSize):
                if self.trail[i][j]:
                    p[i][j]=p[i][j]+100
        print("found")
        Ant.desiredPathNumber=Ant.desiredPathNumber-1
        Ant.paths.append(self.trail)
        self.trail=[[False for i in range(textureSize)] for j in range(textureSize)]
        self.x=start[0]
        self.y=start[1]


    def getdirection(self, p, img):
        if abs(self.x-goal[0])<5 and abs(self.y-goal[1])<5:
            self.reach(p)
            return
        neigh=[[self.x-speed,self.y+speed],[self.x,self.y+speed],[self.x+speed,self.y+speed],
               [self.x-speed,self.y],[self.x+speed,self.y],
               [self.x-speed,self.y-speed],[self.x,self.y-speed],[self.x+speed,self.y-speed]]
        pneigh=[p[self.x-speed][self.y+speed],p[self.x][self.y+speed],p[self.x+speed][self.y+speed],
               p[self.x-speed][self.y],p[self.x+speed][self.y],
               p[self.x-speed][self.y-speed],p[self.x][self.y-speed],p[self.x+speed][self.y-speed]]
        suma=0
        for i in range(8):
            if(neigh[i][0] < textureSize-speed*2 and neigh[i][1] < textureSize-speed*2 and neigh[i][0] > speed and neigh[i][1] > speed and img[neigh[i][0],neigh[i][1]]==255):
                suma=suma+pneigh[i]
            else:
                pneigh[i]=0
        if suma<=0:
            self.x=self.px
            self.y=self.py
            return
        else:
            self.px=self.x
            self.py=self.y
        tmp=random.randint(0, suma-1)
        i=0
        while tmp>0:
            tmp=tmp-pneigh[i]
            i=i+1
        i=i-1
        self.x=neigh[i][0]
        self.y=neigh[i][1]
        self.trail[self.x][self.y]=True
        return


    def move(self, pheromones, img):
        self.getdirection(pheromones, img)    

# Znajdź szerokość trasy w danym punkcie dla zbinaryzowanej mapy drogowej
def getRoadWidth(road_map_bin, coordinates):
    
    R = 1
    segments_count = 0
    first_segment_found_iteration = -1 # moment "pojawienia się" pierwszego segmentu
    current_iteration = 0
    
    # część wspólna brzegów i okręgu, dopóki nie istnieją co najmniej 2 segmenty
    while segments_count < 2:

        # pusty obrazek o analogicznych wymiarach, co mapa
        road_map_frame = np.zeros(road_map_bin.shape, np.uint8)

        # rysowanie okręgu o promieniu R
        cv2.circle(road_map_frame, coordinates, R, (255,255,255), -1 );

        # część wspólna z brzegami przy drodzę
        road_map_circle_XOR = cv2.bitwise_xor(road_map_bin, road_map_frame)
        intersection = cv2.bitwise_and(road_map_circle_XOR, road_map_frame)

        # segmentacja części wspólnej i zapisanie ilość znalezionych segmentów
        contours, hierarchy = cv2.findContours(intersection[:,:,0], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # zliczanie znalezionych konturów
        segments_count = len(contours)

        # sprawdzanie, czy pojawił się pierwszy kontur
        if segments_count == 1 and first_segment_found_iteration == -1:
            first_segment_found_iteration = current_iteration

        current_iteration = current_iteration + 1
        R = R + 1

    # Sprawdzanie, czy oba segmenty zostały znalezione jednocześnie
    if first_segment_found_iteration == -1:
        first_segment_found_iteration = current_iteration

    # Policzenie szerokości trasy w danym koordynacie
    return (current_iteration - 1)*2 - (current_iteration - first_segment_found_iteration - 1)   