var fileName = "";
var selectedFile;
let pyodide;
let imageArray;
let chosenPoints = [];
let imageFile = new FileReader();

async function handleFileUpload() {
    var fileInput = document.getElementById('fileUpload');
    selectedFile = fileInput.files[0];
    fileName = selectedFile.name;

    const img = document.getElementById("previewImage");
    img.src = URL.createObjectURL(selectedFile);
    img.style.display = "block";
}

function choosePoints(e) {
    let rect = e.currentTarget.getBoundingClientRect();
    let x = Math.round(e.clientX - rect.left);
    let y = Math.round(e.clientY - rect.top);
    console.log("x: " + x + ", y: " + y);
    validatePoints(x, y);
}
function loadZip(fr) {
    pyodide.unpackArchive(fr.result, "zip");
}

async function validatePoints(x, y) {
    pyodide = await loadPyodide();
    await pyodide.loadPackage("opencv-python");
    await pyodide.loadPackage("matplotlib");
    console.log(selectedFile)

    var zip = new JSZip();
    zip.file(fileName, selectedFile);
    zip.generateAsync({ type: "base64" }).then(async function (base64) {
        const url = 'data:application/zip;base64,' + base64;
        fetch(url)
            .then(res => res.blob())
            .then(blob => {
                imageFile = new FileReader();
                imageFile.readAsArrayBuffer(blob);
                setTimeout(() => loadZip(imageFile), 1500);
            })
    });

    var pythonCode = `
    from pyodide.http import pyfetch
    import cv2
    import os
    
    print(os.getcwd())
    print(os.listdir())
    print(os.listdir(os.getcwd()))
    tab = cv2.imread("${fileName}")
    `;

    await new Promise(done => setTimeout(() => done(), 1600));
    pyodide.runPython(pythonCode);
    console.log(pyodide.globals.get("tab"));

    var pythonCode_1 = `
    import cv2
    import numpy as np
    import os
    def convert_to_binary_array(path):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        kernel = np.ones((5,5),np.uint8)
        img = cv2.dilate(img,kernel,iterations = 1)
        thresh, im_bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return im_bw
    
    image = convert_to_binary_array('${fileName}')
    print(os.listdir(os.getcwd()))
    `;

    pyodide.runPython(pythonCode_1);
    imageArray = pyodide.globals.get("image").toJs();

    console.log(imageArray);
    console.log(imageArray[y][x]);
    if(imageArray[y][x] === 0) {
        alert("Wybrano punkt spoza drogi");
    }
    else {
        chosenPoints.push([x,y]);
        console.log(chosenPoints);
        if(chosenPoints.length === 1) {
            let start = document.getElementById("startPoint");
            start.innerText = `(${chosenPoints[0][0]}, ${chosenPoints[0][1]})`
            start.style.display = "inline-block";
        }
        if(chosenPoints.length === 2) {
            let end = document.getElementById("endPoint");
            end.innerText = `(${chosenPoints[1][0]}, ${chosenPoints[1][1]})`
            end.style.display = "inline-block";
        }
    }
}

async function calculatePath() {
    await pyodide.loadPackage("pandas")
    await pyodide.loadPackage("opencv-python");
    await pyodide.loadPackage("matplotlib");
    await pyodide.loadPackage("numpy");
    await pyodide.loadPackage("pillow");

    var pythonCode = `
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    from matplotlib import pyplot
    import random
    import pandas as pd
    import os
    from PIL import Image
    import io, base64
    
    print(os.listdir(os.getcwd()))
    
    antNumber=125

    start= ${chosenPoints[0]}
   
    goal = ${chosenPoints[1]}
    
    speed=4
    
    imageName='${fileName}'
    
    #rozmiar obrazu powyżej (nie dawać więcej niż 512 bo nie testowane)
    textureSize=512
    best=np.zeros((512,512), np.uint8)
    img_str = ""
    
    def calculate_shortest_path():
        img = convert_to_binary_array(imageName)
        ants=[Ant(start[0],start[1]) for i in range(antNumber)]
        tmp=round(textureSize*math.sqrt(2))
        pheromones = [[tmp-round(math.sqrt(math.pow(i-goal[0],2)+math.pow(j-goal[1],2))) for j in range(textureSize)] for i in range(textureSize)]
        while (Ant.desiredPathNumber>0):
            for i in range(len(ants)):
                ants[i].move(pheromones, img)
    
        # wczytanie mapy
        road_map = cv2.imread(imageName, cv2.COLOR_BGR2GRAY)
    
        # # binaryzacja mapy
        _, road_map_bin = cv2.threshold( road_map, 126, 255, cv2.THRESH_BINARY )
    
        best=np.zeros((512,512), np.uint8)
        for loaded_input in Ant.paths:
            # wczytanie współrzędnych wskazujących punkty trasy
            all_road_coordinates = []
            for x in range(len(loaded_input[0])):
                for y in range(len(loaded_input[0])):
                    if loaded_input[x][y]:
                        all_road_coordinates.append([x,y])
    
            # output w takiej samej formie, co input, ale z wartościami będącymi szerokością trasy
            output = np.zeros((512,512), np.uint8)
            for coordinates in all_road_coordinates:
                X, Y = coordinates
                output[X,Y] = getRoadWidth(road_map_bin,coordinates)
            if np.sum(output)<np.sum(best) or np.sum(best)==0:
                best=output
            
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
    
    calculate_shortest_path()
    `;

    pyodide.runPython(pythonCode);
    console.log(pyodide.globals.get("best").toJs());
    var blob = new Blob([pyodide.globals.get("best").toJs()], {type: "image/jpg"});
    var url = URL.createObjectURL(blob);

    const img = document.getElementById("resultImage");
    img.src = url;
    img.style.display = "block";
}