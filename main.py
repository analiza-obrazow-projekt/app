import asyncio
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


# pyodide.register_js_function(load_image)
#liczba mrówek szukających celu (nie przesadzać za względu na ograniczenia pamięci każda to jedna tablica 512x512 booli)
antNumber=125

#punkt z którego mrówki zaczynają (jeśli na polu czarnym mrówki pozostaną w miejscu)
start= [62,504]

#punkt docelowy
goal = [443,56]
# start= [200, 404]
# goal = [62,504]
# start= [62,504]
# goal = [443,56]

#prędkość poruszania (różnica w pikselach)
speed=4

#obraz - nazwa pliku
imageName="test.jpg"

#rozmiar obrazu powyżej (nie dawać więcej niż 512 bo nie testowane)
textureSize=512

def calculateShortestPath():

    ants=[Ant(start[0],start[1]) for i in range(antNumber)]
    tmp=round(textureSize*math.sqrt(2))
    pheromones = [[tmp-round(math.sqrt(math.pow(i-goal[0],2)+math.pow(j-goal[1],2))) for j in range(textureSize)] for i in range(textureSize)]
    img = convert_to_binary_array(imageName)
    tmp=np.transpose(img)
    while (Ant.desiredPathNumber>0):
        for i in range(len(ants)):
            ants[i].move(pheromones, img)
    #TODO: Logic to calculate the shortest path

    for j in range(512):
        d=[i for i in Ant.paths[0][j] if i]
        print(d)
    drawResult()
    readFile("test.jpg")
    showImage()
             
    
def drawResult():
    fig, ax = plt.subplots()
    # x axis
    x = ["Python", "C++", "JavaScript", "Golang"]
    # y axis
    y = [10, 5, 9, 7]
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    # Naming the x-label
    plt.xlabel('Language')
    # Naming the y-label
    plt.ylabel('Score')
    
    # Naming the title of the plot
    plt.title('Language vs Score')
    display(fig,target="matplotlib-lineplot")
    

def fileUpload():
    print("upload file")

def readFile(filename):
    display("wczytana tablica",target="matplotlib-lineplot")
    display(cv2.imread(filename),target="matplotlib-lineplot")

def showImage():
    fig, ax = plt.subplots()
    plt.imshow(cv2.imread("test.jpg"))
    display("wczytany obraz",target="matplotlib-lineplot")
    display(fig, target="matplotlib-lineplot")

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