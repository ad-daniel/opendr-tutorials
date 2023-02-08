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

from controller import Supervisor, Display, Camera
from opendr.engine.data import Image
from opendr.perception.object_detection_2d import NanodetLearner
import numpy as np
import os
import base64

TIMESTEP = 64
DISPLAY_IMAGE_PATH = os.getcwd() + '/display.jpg'
LOCATIONS = {
    'Keyboard': [-0.7, 0.5, 0.52],
    'Laptop': [-0.58, 0.5, 0.5],
    'BeerBottle': [-0.42, 0.49, 0.5],
    'Cat': [-0.57, 0.40, 0.56],
    'FlowerPot': [-0.71, 0.49, 0.53],
    'Clock': [-0.54, 0.46, 0.67],
    'TennisRacket': [-0.53, 0.42, 0.62]
}


def send_image_to_display(robot, display):
    display.imageSave(None, DISPLAY_IMAGE_PATH)
    with open(DISPLAY_IMAGE_PATH, 'rb') as f:
        fileString64 = base64.b64encode(f.read()).decode()
        robot.wwiSendText('image[display]]:data:image/jpeg;base64,' + fileString64)


def handle_wwi_messages():
    global current_object
    message = robot.wwiReceiveText()
    while message:
        if message.startswith('spawn:'):
            name = message[6:]
            if current_object:  # hide current object
                robot.getFromDef(current_object).getField('translation').setSFVec3f([0, 0, -2])
            current_object = name.upper()
            robot.getFromDef(current_object).getField('translation').setSFVec3f(LOCATIONS[name])
        elif message.startswith('noise:'):
            noise_field.setSFFloat(float(message[6:]))
        elif message.startswith('radial-coefficient:'):
            value = [float(x) for x in message[19:].split(',')]
            lens_field.setSFVec2f(value)
        elif message.startswith('light-position:'):
            current_position = light_translation_field.getSFVec3f()
            light_translation_field.setSFVec3f([float(message[15:]), current_position[1], current_position[2]])
        elif message.startswith('light-color:'):
            value = [float(x) for x in message[12:].split(',')]
            light_color_field.setSFColor(value)
        message = robot.wwiReceiveText()


robot = Supervisor()

# enable devices
camera = Camera('camera')
camera.enable(2 * TIMESTEP)
width, height = camera.getWidth(), camera.getHeight()

display = robot.getDevice('display')
display.setFont('Lucida Console', 16, True)

# get node/field references
camera_node = robot.getFromDef('CAMERA')
noise_field = camera_node.getField('noise')
lens_field = camera_node.getField('lens').getSFNode().getField('radialCoefficients')
current_detection = None

light_node = robot.getFromDef("LIGHT")
light_translation_field = light_node.getField('translation')
light_color_field = light_node.getField('pointLightColor')

robot.step(TIMESTEP)

# prepare Nanodet learner
learner = NanodetLearner(model_to_use='m', device='cpu')
learner.load("./nanodet_m", verbose=True)
print(learner.classes)
current_object = None

while robot.step(TIMESTEP) != -1:
    handle_wwi_messages()  # handle messages from robot window

    image = camera.getImage()
    frame = np.frombuffer(image, np.uint8).reshape((height, width, 4))

    if current_detection:
        # erase the previous drawing by setting the pixels alpha value to 0 (transparent).
        display.setAlpha(0.0)
        display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])
        current_detection = None

    # detect objects
    result = learner.infer(input=Image(frame))

    # copy raw image into display
    ir = display.imageNew(image, Display.BGRA, width, height)
    display.imagePaste(ir, 0, 0, False)

    for box in result:
        bounding_box = box.coco()
        if learner.classes[bounding_box['category_id']] == 'dining_table' or float(box.confidence) < 0.5:
            continue
        # draw detection box in the display image
        current_detection = bounding_box['bbox']
        display.setAlpha(1.0)
        display.setColor(0x00FFFF)
        display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])
        display.drawText(learner.classes[bounding_box['category_id']], current_detection[0], current_detection[1] - 20)
        display.setColor(0xFF0000)

        # print('class:', learner.classes[bounding_box['category_id']], 'confidence:', box.confidence)

    send_image_to_display(robot, display)
    display.imageDelete(ir)

# cleanup
if (os.path.exists(DISPLAY_IMAGE_PATH)):
    os.remove(DISPLAY_IMAGE_PATH)
