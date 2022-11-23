FROM cyberbotics/webots.cloud:R2022b-ubuntu20.04
ARG PROJECT_PATH
RUN mkdir -p $PROJECT_PATH
RUN apt update && apt install python3.8-venv libfreetype6-dev git build-essential cmake python3-dev wget libopenblas-dev libsndfile1 libboost-dev libeigen3-dev wheel
RUN python3 -m pip install opendr-toolkit-engine opendr-toolkit-object-detection-2d