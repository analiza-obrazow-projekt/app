var fileName = "";
var selectedFile;
let pyodide;

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
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
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
    zip.file("test.jpg", selectedFile);
    zip.generateAsync({ type: "base64" }).then(async function (base64) {
        const url = 'data:application/zip;base64,' + base64;
        fetch(url)
            .then(res => res.blob())
            .then(blob => {
                    let fr = new FileReader();
                    fr.readAsArrayBuffer(blob);
                    setTimeout(() => loadZip(fr), 1500);
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
}