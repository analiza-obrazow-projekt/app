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
import pyodide

def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    thresh, im_bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return im_bw

# pyodide.register_js_function(load_image)

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
    fi = form['filename']
    if fi.filename:
	    # This code will strip the leading absolute path from your file-name
        load_image(os.path.basename(fi.filename))    
    print("FILEUPLOAD")

