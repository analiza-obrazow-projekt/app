import asyncio
import base64
import cv2
import json
import js
import numpy as np
import pyscript
from pyodide.http import pyfetch
from js import document
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
import os

async def calculateShortestPath():
    #TODO: Logic to calculate the shortest path
    print('Calculating shortest path')
    print('Your open-cv version is:')
    print(cv2.__version__)
    
def drawResult():
   x_values = [1, 2, 3, 4, 5]
   y_values = [2, 4, 6, 8, 10]
   x = plt.plot(x_values, y_values)
   plt.show(x)

def fileUpload():
    print("upload file")