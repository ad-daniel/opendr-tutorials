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


models = {
    'Keyboard': 'translation -0.7 0.5 0.52 rotation 0 1 0 -0.12',
    'Laptop': 'translation -0.58 0.5 0.5 rotation 0 0 1 -2.16 controller "<none>"',
    'BeerBottle': 'translation -0.58 0.5 0.5 rotation 0 1 0 0',
    'Cat': 'translation -0.62 0.46 0.56 rotation 0 0 1 -2.88 scale 0.75',
    'SoccerBall': 'translation 0 0 0 rotation 0 1 0 0',
    'FlowerPot': 'translation -0.71 0.49 0.53 rotation 0 1 0 0',
    'Clock': 'translation -0.54 0.46 0.67 rotation 0 0 1 2.618',
    'Book': 'translation -0.51 0.52 0.51 rotation -0.12 -1 -0.12 1.58',
}


def spawn_object(name):
    # remove existing node
    target = robot.getFromDef('TARGET')
    if target:
        target.remove()
    # spawn new object
    root_children_field.importMFNodeFromString(-1, f'DEF TARGET {name} {{ {models[name]} }}')


def send_image_to_display(robot, display):
    """Send display image to the robot window"""
    print('SAVING IMAGE TO:', display_image_path)
    display.imageSave(None, display_image_path)

    if os.path.exists(display_image_path):
        print('IMAGE CREATED')
    else:
        print('IMAGE NOT SAVED')

    with open(display_image_path, 'rb') as f:
        fileString64 = base64.b64encode(f.read()).decode()
        robot.wwiSendText('image[display]]:data:image/jpeg;base64,' + fileString64)


display_image_path = os.getcwd() + '/display.jpg'

robot = Supervisor()
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

root_node = robot.getRoot()
root_children_field = root_node.getField('children')

camera_node = robot.getFromDef("CAMERA")
noise_field = camera_node.getField('noise')

current_detection = None
while robot.step(timestep) != -1:
    image = camera.getImage()

    print('HERE')

    # retrieve messages from robot window
    message = robot.wwiReceiveText()
    while message:
        if message.startswith('spawn:'):
            spawn_object(message[6:])
        elif message.startswith('noise:'):
            print(message)
            noise_field.setSFFloat(float(message[6:]))

        message = robot.wwiReceiveText()

    if image:
        frame = np.frombuffer(image, np.uint8).reshape((height, width, 4))
        frame = frame[:, :, :3]
        (h, w) = frame.shape[:2]

        if current_detection:
            # erase the previous drawing by setting the pixels alpha value to 0 (transparent).
            display.setAlpha(0.0)
            display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])
            current_detection = None

        img = Image(frame)
        boxes = learner.infer(input=img)
        if len(boxes) > 0:
            bb = boxes[0].coco()
            current_detection = bb['bbox']

            ir = display.imageNew(image, Display.BGRA, width, height)
            display.imagePaste(ir, 0, 0, False)

            for i in range(len(boxes)):
                if learner.classes[bb['category_id']] == 'dining_table' or float(boxes[i].confidence) < 0.5:
                    continue

                # show detection in the display
                display.setAlpha(1.0)
                display.setColor(0x00FFFF)
                display.drawRectangle(current_detection[0], current_detection[1], current_detection[2], current_detection[3])
                display.drawText(learner.classes[bb['category_id']], current_detection[0], current_detection[1] - 20)
                display.setColor(0xFF0000)

                #print('bounding box:', bb['bbox'])
                print('class:', learner.classes[bb['category_id']], 'confidence:', boxes[0].confidence)

            send_image_to_display(robot, display)
            display.imageDelete(ir)

# cleanup
if (os.path.exists(display_image_path)):
    os.remove(display_image_path)
