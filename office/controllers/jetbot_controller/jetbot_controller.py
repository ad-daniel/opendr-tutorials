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

from opendr.engine.data import Image
from opendr.perception.object_detection_2d import NanodetLearner
from opendr.perception.object_detection_2d import draw_bounding_boxes
import cv2
import numpy as np

robot = Robot()
timestep = int(robot.getBasicTimeStep())

learner = NanodetLearner(model_to_use='m', device='cpu')
learner.load("./nanodet_m", verbose=True)

camera = Camera("camera")
camera.enable(2 * timestep)
print(camera.getWidth(), camera.getHeight(), learner.classes)

while robot.step(timestep) != -1:
    image = camera.getImage()
    if image:
        frame = np.frombuffer(image, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
        frame = frame[:, :, :3]
        (h, w) = frame.shape[:2]

        img = Image(frame)
        boxes = learner.infer(input=img)
        if len(boxes) > 0:
            bb = boxes[0].coco()
            print('bounding box:', bb['bbox'])
            print('class:', learner.classes[bb['category_id']], 'confidence:', boxes[0].confidence)
            out = draw_bounding_boxes(img.opencv(), boxes, class_names=learner.classes)
            cv2.imwrite('test.jpg', out)
