import RobotWindow from 'https://cyberbotics.com/wwi/R2023a/RobotWindow.js';

window.buttonCallback =  function(obj) {
  const collection = document.getElementsByClassName("spawner-option");
  for (let i = 0; i < collection.length; ++i) {
    collection[i].style.background = "white"
  }

  obj.style.background = "cyan";

  console.log('spawn:' + obj.innerText);
  window.robotWindow.send('spawn:' + obj.innerText);
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