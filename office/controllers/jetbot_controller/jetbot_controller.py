# Copyright 1996-2022 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from controller import Robot, Display, Camera, Node

from opendr.engine.data import Image
from opendr.perception.object_detection_2d import NanodetLearner
from opendr.perception.object_detection_2d import draw_bounding_boxes
import cv2
import numpy as np
import os
import base64


def cleanup():
    """Remove device image files."""
    try:
        os.remove(deviceImagePath + '/camera.jpg')
    except OSError:
        pass


def sendDeviceImage(robot, device):
    """Send the rendering device image to the robot window."""
    if device.getNodeType() == Node.DISPLAY:
        deviceName = 'display'
        fileName = deviceName + '.jpg'
        device.imageSave(None, deviceImagePath + '/' + fileName)
    else:
        return

    with open(deviceImagePath + '/' + fileName, 'rb') as f:
        fileString = f.read()
        fileString64 = base64.b64encode(fileString).decode()
        robot.wwiSendText("image[" + deviceName + "]:data:image/jpeg;base64," + fileString64)


deviceImagePath = os.getcwd()

robot = Robot()
timestep = int(robot.getBasicTimeStep())

learner = NanodetLearner(model_to_use='m', device='cpu')
learner.load("./nanodet_m", verbose=True)

camera = Camera("camera")
camera.enable(2 * timestep)
print(camera.getWidth(), camera.getHeight(), learner.classes)

# Get the display device.
display = robot.getDevice('display')
display.setFont('Lucida Console', 15, True)
#display.setColor(0xFF0000)

current_bbox = None
print('start main loop')
while robot.step(timestep) != -1:
    image = camera.getImage()

    if image:
        frame = np.frombuffer(image, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
        frame = frame[:, :, :3]
        (h, w) = frame.shape[:2]

        if current_bbox:
          # Erase the previous drawing by setting the pixels alpha value to 0 (transparent).
          display.setAlpha(0.0)
          display.drawRectangle(current_bbox[0], current_bbox[1], current_bbox[2], current_bbox[3])

        img = Image(frame)
        boxes = learner.infer(input=img)
        if len(boxes) > 0:
            bb = boxes[0].coco()
            current_bbox = bb['bbox']
            # Show detected blob in the display: draw the circle and centroid.
            ir = display.imageNew(image, Display.BGRA, camera.getWidth(), camera.getHeight())
            display.imagePaste(ir, 0, 0, False)
            display.setAlpha(1.0)
            display.setColor(0x00FFFF)
            display.drawRectangle(current_bbox[0], current_bbox[1], current_bbox[2], current_bbox[3])
            display.drawText(learner.classes[bb['category_id']], current_bbox[0], current_bbox[1] - 20)
            display.setColor(0xFF0000)

            sendDeviceImage(robot, display)
            display.imageDelete(ir)

            print('bounding box:', bb['bbox'])
            print('class:', learner.classes[bb['category_id']], 'confidence:', boxes[0].confidence)
            #out = draw_bounding_boxes(img.opencv(), boxes, class_names=learner.classes)
            #cv2.imwrite('test.jpg', out)


# Cleanup code.
cleanup()
