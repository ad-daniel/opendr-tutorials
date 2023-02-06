FROM cyberbotics/webots.cloud:R2022b-ubuntu20.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
COPY . $PROJECT_PATH
RUN apt update && apt --option="APT::Acquire::Retries=3" install -y git python3-dev python3-pip libfreetype6-dev build-essential cmake python3-dev wget libopenblas-dev libsndfile1 libboost-dev && python3 -m pip install wheel protobuf==3.20.0 onnx==1.8.0 opendr-toolkit-engine git+https://github.com/cocodataset/panopticapi.git#egg=panopticapi && python3 -m pip install opendr-toolkit-object-detection-2d