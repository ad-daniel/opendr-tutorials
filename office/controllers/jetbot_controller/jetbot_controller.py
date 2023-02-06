# Copyright 1996-2023 Cyberbotics Ltd.
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

from controller import Robot, Display, Camera
from opendr.engine.data import Image
from opendr.perception.object_detection_2d import NanodetLearner
import numpy as np
import os
import base64


def sendDisplayImage(robot, display):
    """Send display image to the robot window"""
    display.imageSave(None, displayImagePath)

    with open(displayImagePath, 'rb') as f:
        fileString64 = base64.b64encode(f.read()).decode()
        robot.wwiSendText('image[display]]:data:image/jpeg;base64,' + fileString64)


displayImagePath = os.getcwd() + '/display.jpg'

robot = Robot()
timestep = int(robot.getBasicTimeStep())

learner = NanodetLearner(model_to_use='m', device='cpu')
learner.load("./nanodet_m", verbose=True)

camera = Camera("camera")
camera.enable(2 * timestep)
width, height = camera.getWidth(), camera.getHeight()
print(width, height, learner.classes)

# Get the display device.
display = robot.getDevice('display')
display.setFont('Lucida Console', 15, True)

current_detection = None
while robot.step(timestep) != -1:
    image = camera.getImage()

    if image:
        frame = np.frombuffer(image, np.uint8).reshape((height, width, 4))
        frame = frame[:, :, :3]
        (h, w) = frame.shape[:2]

        if current_detection:
            # erase the previous drawing by setting the pixels alpha value to 0 (transparent).
            display.setAlpha(0.0)
            display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])

        img = Image(frame)
        boxes = learner.infer(input=img)
        if len(boxes) > 0:
            bb = boxes[0].coco()
            current_detection = bb['bbox']

            # show detection in the display
            ir = display.imageNew(image, Display.BGRA, width, height)
            display.imagePaste(ir, 0, 0, False)
            display.setAlpha(1.0)
            display.setColor(0x00FFFF)
            display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])
            display.drawText(learner.classes[bb['category_id']], current_detection[0], current_detection[1] - 20)
            display.setColor(0xFF0000)

            sendDisplayImage(robot, display)
            display.imageDelete(ir)

            print('bounding box:', bb['bbox'])
            print('class:', learner.classes[bb['category_id']], 'confidence:', boxes[0].confidence)

# cleanup
if (os.path.exists(displayImagePath)):
    os.remove(displayImagePath)
