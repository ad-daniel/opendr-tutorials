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

from controller import Robot, Camera
import numpy as np

from opendr.engine.data import Image
from opendr.perception.object_detection_2d import RetinaFaceLearner

robot = Robot()
timestep = int(robot.getBasicTimeStep())

learner = RetinaFaceLearner(backbone='resnet', device='cuda')
learner.download('.', mode='pretrained')
learner.load('./retinaface_{}'.format('resnet'))

left_motor = robot.getDevice("wheel_left_joint")
right_motor = robot.getDevice("wheel_right_joint")

left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

camera = Camera("camera")
camera.enable(2 * timestep)

# main loop
while robot.step(timestep) != -1:
    left_motor.setVelocity(1)
    right_motor.setVelocity(-1)

    image = camera.getImage()
    if not image:
        continue

    frame = np.frombuffer(image, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
    bounding_boxes = learner.infer(Image(frame))
    if len(bounding_boxes) > 0:
        # print(bounding_boxes.mot()[0][5])
        print(bounding_boxes.mot())
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
