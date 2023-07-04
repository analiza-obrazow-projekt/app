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