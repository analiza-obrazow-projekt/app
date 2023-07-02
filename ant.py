#!/usr/bin/python3
#pip3 install kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
import math
import numpy as np
import cv2
from matplotlib import pyplot
import random

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

def print_image(img):
    pyplot.imshow(img)

antNumber=125
start= [62,504]
goal = [443,56]
# start= [200, 404]
# goal = [62,504]
# start= [62,504]
# goal = [443,56]
speed=4
imageName="starting_image.png"
textureSize=512

class Ant:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.trail=[[False for i in range(textureSize)] for j in range(textureSize)]
        self.px=x
        self.py=y
        self.radius=3

    def reach(self, p):
        for i in range(textureSize):
            for j in range(textureSize):
                if self.trail[i][j]:
                    p[i][j]=p[i][j]+100
        print("found")
        # with open('img.csv', 'w') as file:
        #     for i in range(512):
        #         for j in range(512):
        #             if self.trail[i][j]:
        #                 file.write("1")
        #             else:
        #                 file.write("0")
        #             file.write(" ")
        #         file.write("\n")
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
        tmp=np.min(pneigh)
        #pneigh=[i-tmp+1 for i in pneigh]
        #print(pneigh)
        suma=0
        for i in range(8):
            if(neigh[i][0] < textureSize-speed*2 and neigh[i][1] < textureSize-speed*2 and neigh[i][0] > speed and neigh[i][1] > speed and img[neigh[i][0],neigh[i][1]]==255):
                suma=suma+pneigh[i]
            else:
                pneigh[i]=0
        # neigh=[neigh[i] for i in range(8) if pneigh[i]]
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
            # print(i)
        i=i-1
        # print(i)
        # print("len"+str(len(neigh)))
        self.x=neigh[i][0]
        self.y=neigh[i][1]
        self.trail[self.x][self.y]=True
        return


    def move(self, pheromones, img):
        self.getdirection(pheromones, img)

    def draw(self, canvas):
        with canvas:
            Color(0,0,1)
            Ellipse(pos=(self.x - self.radius, self.y - self.radius),
                        size=(self.radius * 2, self.radius * 2))

class CircleWidget(Widget):
    def __init__(self, **kwargs):
        super(CircleWidget, self).__init__(**kwargs)
        self.ants=[Ant(start[0],start[1]) for i in range(antNumber)]
        self.loop_interval = 1/60
        self.loop_event = None
        tmp=round(textureSize*math.sqrt(2))
        self.pheromones = [[tmp-round(math.sqrt(math.pow(i-goal[0],2)+math.pow(j-goal[1],2))) for j in range(textureSize)] for i in range(textureSize)]
        self.img = convert_to_binary_array(imageName)
        self.texture = Texture.create(size=(textureSize, textureSize))
        tmp=np.transpose(self.img)
        self.texture.blit_buffer(tmp.flatten(), colorfmt='luminance', bufferfmt='ubyte')


    def start_loop(self):
        self.loop_event = Clock.schedule_interval(self.update, self.loop_interval)

    def stop_loop(self):
        if self.loop_event:
            self.loop_event.cancel()
            self.loop_event = None

    def redraw(self, *args):
        for i in range(len(self.ants)):
            self.ants[i].draw(self.canvas)

    def update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Rectangle(texture=self.texture, pos=(0,0), size=(textureSize,textureSize))
        for i in range(len(self.ants)):
            self.ants[i].move(self.pheromones, self.img)
        self.redraw()

class CircleApp(App):
    def build(self):
        loop_widget = CircleWidget()
        loop_widget.start_loop()
        return loop_widget


if __name__ == '__main__':
    CircleApp().run()