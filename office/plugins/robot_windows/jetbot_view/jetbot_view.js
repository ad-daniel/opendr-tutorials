import RobotWindow from 'https://cyberbotics.com/wwi/R2023a/RobotWindow.js';

const DEFAULT_LOCATIONS = {
  'Keyboard': {'translation': [-0.6, 0.5, 0.53], 'rotation': [0, 1, 0, -0.12]},
  'Laptop': {'translation': [-0.58, 0.5, 0.5], 'rotation': [0, 0, 1, -2.16]},
  'BeerBottle': {'translation': [-0.42, 0.49, 0.5], 'rotation': [0, 0, 1, -2.16]},
  'Cat': {'translation': [-0.57, 0.40, 0.56], 'rotation': [0, 0, 1, 2.62]},
  'FlowerPot': {'translation': [-0.67, 0.51, 0.53], 'rotation': [0, 0, 1, 0]},
  'Clock': {'translation': [-0.54, 0.46, 0.67], 'rotation': [0, 0, 1, 2.62]},
  'TennisRacket': {'translation': [-0.53, 0.42, 0.62], 'rotation': [-0.07, -0.8, -0.6, 1.04]},
}

window.spawnerButtonCallback =  function(obj) {
  if (obj.style.background === "cyan") {
    obj.style.background = "white"
    window.robotWindow.send(`${obj.innerText}:0,0,-2`);
    const display = document.getElementById('display');
    display.removeChild(document.getElementById(obj.innerText));
  } else {
    obj.style.background = "cyan";

    const t = DEFAULT_LOCATIONS[obj.innerText]['translation'];
    const r = DEFAULT_LOCATIONS[obj.innerText]['rotation'];
    createPositionInput(obj.innerText, t);
    console.log(`${obj.innerText}:${t[0]},${t[1]},${t[2]}|${r[0]},${r[1]},${r[2]},${r[3]}`)
    window.robotWindow.send(`${obj.innerText}:${t[0]},${t[1]},${t[2]}|${r[0]},${r[1]},${r[2]},${r[3]}`);
  }
}

function createPositionInput(name, value) {
  const label = document.createElement('label');
  label.id = name;
  label.innerText = name;

  const x = createCell(name, 0.1, 'number', value[0]);
  const y = createCell(name, 0.1, 'number', value[1]);
  const z = createCell(name, 0.1, 'number', value[2]);

  const display = document.getElementById('display');
  display.appendChild(label);
  display.appendChild(x);
  display.appendChild(y);
  display.appendChild(z);
  display.appendChild(document.createElement('br'))

}

function createCell(name, step, type, value) {
  const input = document.createElement('input');
  input.step = step;
  input.type = type;
  input.value = value;
  input.style = 'width:50px';
  input.onchange = () => positionCallback(name);

  return input;
}

function positionCallback(name) {
  const element = document.getElementById(name);
  console.log(`${name}:${element.children[0].value},${element.children[1].value},${element.children[2].value}`)
  window.robotWindow.send(`${name}:${element.children[0].value},${element.children[1].value},${element.children[2].value}`);
}


window.noiseInputCallback =  function(obj) {

  if (parseFloat(obj.value) > 0.5)
    obj.value = 0.5
  if (parseFloat(obj.value) < 0.0)
    obj.value = 0.0

  console.log(`noise:${obj.value}`)
  window.robotWindow.send(`noise:${obj.value}`);
}

window.lensRadialInputCallback =  function() {
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

window.lightPositionInputCallback =  function(obj) {
  const element = document.getElementById("light-position");
  window.robotWindow.send(`light-position:${element.children[0].value},${element.children[1].value},${element.children[2].value}`);
}

window.objectPositionInputCallback =  function(obj) {
  const element = document.getElementById("object-position");
  window.robotWindow.send(`object-position:${element.children[0].value},${element.children[1].value},${element.children[2].value}`);
}

window.lightIntensityInputCallback =  function(obj) {
  window.robotWindow.send(`light-intensity:${obj.value}`);
}

window.lightColorInputCallback =  function(obj) {
  const red = parseInt(obj.value.substring(1, 3), 16) / 255;
  const green = parseInt(obj.value.substring(3, 5), 16) / 255;
  const blue = parseInt(obj.value.substring(5, 7), 16) / 255;

  console.log(`light-color:${red},${green},${blue}`);
  window.robotWindow.send(`light-color:${red},${green},${blue}`);
}

// Initialize the RobotWindow class in order to communicate with the robot.
window.onload = function() {
  console.log('HTML page loaded.');
  window.robotWindow = new RobotWindow();
  window.robotWindow.setTitle('JetBot robot window');
  window.robotWindow.receive = function(message, robot) {
    // image format: image[<device name>]:<URI image data>
    if (message.startsWith('image')) {
      const label = message.substring(message.indexOf('[') + 1, message.indexOf(']'));
      const imageElement = document.getElementById('robot-' + label);
      if (imageElement != null)
        imageElement.setAttribute('src', message.substring(message.indexOf(':') + 1));
    } else {
      if (message.length > 200)
        message = message.substr(0, 200);
      console.log("Received unknown message for robot '" + robot + "': '" + message + "'");
    }
  };
};