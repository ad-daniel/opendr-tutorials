FROM cyberbotics/webots.cloud:R2022b-ubuntu20.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
COPY . $PROJECT_PATH
RUN sudo apt update && sudo apt install python3 && python3 -m pip install wheel opendr-toolkit-engine opendr-toolkit-object-detection-2d