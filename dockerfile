# syntax=docker/dockerfile:1
FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# --- System deps needed for building a ROS 2 workspace + python venv/pip ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    python3-pip \
    python3-colcon-common-extensions \
    build-essential \
    git \
  && rm -rf /var/lib/apt/lists/*

# --- Workspace layout ---
ENV HOME=/root
ENV WS=${HOME}/vector_ws
ENV VENV_DIR=${WS}/.vector

WORKDIR ${WS}

# Copy repository into the container workspace
# Assumes the repo content is the build context.
COPY . ${WS}/src/vector_ros2

# Récupérer le SDK depuis GitHub et l'installer
RUN git clone --depth 1 https://github.com/rodolphemds/vector-wirepod-python-sdk.git /opt/vector-wirepod-python-sdk && \
    python3 -m pip install --break-system-packages --no-cache-dir /opt/vector-wirepod-python-sdk && \
    rm -rf /opt/vector-wirepod-python-sdk

# SDK configuration
#RUN python3 -m anki_vector.configure
#Before copying the .anki_vector folder to the container, modify sdk_config.ini in it to change the path of the robot certificate. 
COPY .anki_vector/ ${HOME}/.anki_vector/

# Install ROS 2 dependencies declared in package.xml (xacro, robot_state_publisher, etc.)
RUN rosdep update && \
    apt-get update && rosdep install --from-paths "${WS}/src" --ignore-src -y \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex; \
    python3 -m venv --system-site-packages "${VENV_DIR}"; \
    source "${VENV_DIR}/bin/activate"; \
    python3 -m pip install --upgrade pip; \
    export AMENT_TRACE_SETUP_FILES=1; \
    source /opt/ros/jazzy/setup.bash; \
    colcon build --packages-select vector_ros2

# Source ROS + overlay by default in interactive shells
RUN echo "source /opt/ros/jazzy/setup.bash" >> /etc/bash.bashrc && \
    echo "source ${WS}/install/setup.bash" >> /etc/bash.bashrc && \
    echo "source ${VENV_DIR}/bin/activate" >> /etc/bash.bashrc

WORKDIR ${WS}

CMD ["ros2 launch vector_ros2 vector.launch.py"]