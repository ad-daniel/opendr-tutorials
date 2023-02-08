import RobotWindow from 'https://cyberbotics.com/wwi/R2023a/RobotWindow.js';

window.spawnerButtonCallback =  function(obj) {
  const collection = document.getElementsByClassName("spawner-option");
  for (let i = 0; i < collection.length; ++i)
    collection[i].style.background = "white"

  obj.style.background = "cyan";

  console.log('spawn:' + obj.innerText);
  window.robotWindow.send('spawn:' + obj.innerText);
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