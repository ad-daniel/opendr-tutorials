import RobotWindow from 'https://cyberbotics.com/wwi/R2023a/RobotWindow.js';

const DEFAULT_LOCATIONS = {
  'Laptop': { 'translation': [-0.58, 0.5, 0.5], 'rotation': [0, 0, 1, -2.16] },
  'BeerBottle': { 'translation': [-0.42, 0.49, 0.5], 'rotation': [0, 0, 1, -2.16] },
  'Cat': { 'translation': [-0.57, 0.40, 0.56], 'rotation': [0, 0, 1, 2.62] },
  'FlowerPot': { 'translation': [-0.67, 0.3, 0.53], 'rotation': [0, 0, 1, 0] },
  'Clock': { 'translation': [-0.54, 0.46, 0.67], 'rotation': [0, 0, 1, 2.62] },
  'TennisRacket': { 'translation': [-0.53, 0.42, 0.62], 'rotation': [-0.07, -0.8, -0.6, 1.04] },
}

window.spawnerButtonCallback = function (obj) {
  if (obj.style.background === "rgb(36, 113, 163)") {
    obj.style.background = "buttonface"
    const elements = document.getElementsByClassName(obj.innerText);
    while (elements.length > 0)
      elements[0].parentNode.removeChild(elements[0]);
    window.robotWindow.send(`${obj.innerText}:0,0,-2`);
  } else {
    obj.style.background = "rgb(36, 113, 163)";

    const t = DEFAULT_LOCATIONS[obj.innerText]['translation'];
    const r = DEFAULT_LOCATIONS[obj.innerText]['rotation'];
    createPositionInput(obj.innerText, t);
    console.log(`${obj.innerText}:${t[0]},${t[1]},${t[2]}|${r[0]},${r[1]},${r[2]},${r[3]}`)
    window.robotWindow.send(`${obj.innerText}:${t[0]},${t[1]},${t[2]}|${r[0]},${r[1]},${r[2]},${r[3]}`);
  }
}

window.savePicture = function (obj) {
  const element = document.createElement('a');
  element.setAttribute('href', imageData);
  element.setAttribute('download', 'capture.png');

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

window.saveGroundTruth = function (obj) {
  const element = document.createElement('a');
  element.setAttribute('href', groundTruth);
  element.setAttribute('download', 'ground_truth.png');

  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

function createPositionInput(name, value) {
  const span = document.createElement('span');
  span.style.display = 'block';
  span.className = name;

  const label = document.createElement('label');
  label.className = name;
  label.innerText = name;

  const x = createCell(name, 0.1, 'number', value[0], span);
  const y = createCell(name, 0.1, 'number', value[1], span);
  const z = createCell(name, 0.1, 'number', value[2], span);


  const div = document.getElementById('object-controls');
  span.appendChild(label);
  span.appendChild(x);
  span.appendChild(y);
  span.appendChild(z);
  div.appendChild(span);
}

function createCell(name, step, type, value, element) {
  const input = document.createElement('input');
  input.className = name;
  input.step = step;
  input.type = type;
  input.value = value;
  input.style = 'width:50px';
  input.onchange = () => positionCallback(element);

  return input;
}

function positionCallback(element) {
  console.log(`${element.className}:${element.children[1].value},${element.children[2].value},${element.children[3].value}`)
  window.robotWindow.send(`${element.className}:${element.children[1].value},${element.children[2].value},${element.children[3].value}`);
}


window.noiseInputCallback = function (obj) {

  if (parseFloat(obj.value) > 0.5)
    obj.value = 0.5
  if (parseFloat(obj.value) < 0.0)
    obj.value = 0.0

  console.log(`noise:${obj.value}`)
  window.robotWindow.send(`noise:${obj.value}`);
}

window.lensRadialInputCallback = function () {
  const element = document.getElementById("lens-radial-coefficient");

  if (parseFloat(element.children[0].value) > 1.0)
    element.children[0].value = 1.0
  if (parseFloat(element.children[0].value) < 0.0)
    element.children[0].value = 0.0

  if (parseFloat(element.children[1].value) > 1.0)
    element.children[1].value = 1.0
  if (parseFloat(element.children[1].value) < 0.0)
    element.children[1].value = 0.0

  console.log('radial-coefficient:' + element.children[0].value + ',' + element.children[1].value)
  window.robotWindow.send(`radial-coefficient:${element.children[0].value},${element.children[1].value}`);
}

window.lightPositionInputCallback = function (obj) {
  const element = document.getElementById("light-position");
  window.robotWindow.send(`light-position:${element.children[1].value},${element.children[2].value},${element.children[3].value}`);
}


window.lightIntensityInputCallback = function (obj) {
  window.robotWindow.send(`light-intensity:${obj.value}`);
}

window.lightColorInputCallback = function (obj) {
  const red = parseInt(obj.value.substring(1, 3), 16) / 255;
  const green = parseInt(obj.value.substring(3, 5), 16) / 255;
  const blue = parseInt(obj.value.substring(5, 7), 16) / 255;

  console.log(`light-color:${red},${green},${blue}`);
  window.robotWindow.send(`light-color:${red},${green},${blue}`);
}

let imageData;
let groundTruth;

// Initialize the RobotWindow class in order to communicate with the robot.
window.onload = function () {
  console.log('HTML page loaded.');
  window.robotWindow = new RobotWindow();
  window.robotWindow.setTitle('JetBot robot window');
  window.robotWindow.receive = function (message, robot) {
    // image format: image[<device name>]:<URI image data>
    if (message.startsWith('image')) {
      const label = message.substring(message.indexOf('[') + 1, message.indexOf(']'));
      const imageElement = document.getElementById('robot-' + label);
      imageData = message.substring(message.indexOf(':') + 1);
      if (imageElement != null)
        imageElement.setAttribute('src', imageData);
    } else if (message.startsWith('ground-truth')) {
      groundTruth = message.substring(message.indexOf(':') + 1);
    } else {
      if (message.length > 200)
        message = message.substr(0, 200);
      console.log("Received unknown message for robot '" + robot + "': '" + message + "'");
    }
  };
};