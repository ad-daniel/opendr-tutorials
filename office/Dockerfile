FROM cyberbotics/webots.cloud:R2022b-ubuntu20.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
COPY . $PROJECT_PATH
RUN apt update && apt install -y python3-dev python3-pip libfreetype6-dev build-essential cmake python3-dev wget libopenblas-dev libsndfile1 libboost-dev && python3 -m pip install wheel protobuf==3.20.0 opendr-toolkit-engine && python3 -m pip install opendr-toolkit-object-detection-2d