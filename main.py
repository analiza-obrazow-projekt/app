import asyncio
import base64
import cv2
import json
import js
import numpy as np
import pyscript
from pyscript import display
from pyodide.http import pyfetch
from js import document
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import math
from matplotlib import pyplot
import random
from io import BytesIO


def calculateShortestPath():
    #TODO: Logic to calculate the shortest path
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

