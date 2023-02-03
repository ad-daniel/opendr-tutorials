FROM cyberbotics/webots.cloud:R2022b-ubuntu20.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
COPY . $PROJECT_PATH
RUN apt update && apt install -y python3 python3-pip && python3 -m pip install wheel opendr-toolkit-engine && python3 -m pip install opendr-toolkit-object-detection-2d