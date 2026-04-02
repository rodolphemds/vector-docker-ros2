# syntax=docker/dockerfile:1

FROM osrf/ros:jazzy-desktop-full

# Clean up default users and upgrade system
RUN userdel -r ubuntu || true
RUN apt-get update && apt-get upgrade -y

# Outils de base + X11 libs + Mesa (OpenGL logiciel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    mesa-utils \
    x11-apps \
    libgl1 \
    libgl1-mesa-dri \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    libasound2t64 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN BASHRC_PATH="/root/.bashrc" \
    && ROS_SOURCE_LINE='if [ -n "$ROS_DISTRO" ] && [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then source "/opt/ros/${ROS_DISTRO}/setup.bash"; fi' \
    && grep -qxF "$ROS_SOURCE_LINE" "$BASHRC_PATH" \
    || echo "$ROS_SOURCE_LINE" >> "$BASHRC_PATH"

SHELL ["/bin/bash", "-lc"]

# --- System deps needed for building a ROS 2 workspace + python venv/pip ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    python3-pip \
    python3-tk \
    python3-rosdep \
    python3-colcon-common-extensions \
    ros-jazzy-rclpy \
    ros-jazzy-ros2cli \
    ros-jazzy-foxglove-bridge \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    build-essential \
    git \
  && rm -rf /var/lib/apt/lists/*

# --- Workspace layout ---
ENV HOME=/root
ENV WS=/ros_workspace
ENV VENV_DIR=/root/vector_ros2_venv
ENV ANKI_SDK_CONFIG_DIR=/root/sdk_vector_config

WORKDIR ${WS}

# Create ROS log directory (owned by root)
RUN mkdir -p /root/.ros/log

# Build the ROS overlay workspace inside the image.
# NOTE: This lives outside the persistent /root volume, so it is not masked.
COPY vector-docker-ros2/src/ ${WS}/src/

RUN source /opt/ros/jazzy/setup.bash \
  && rosdep init 2>/dev/null || true \
  && rosdep update \
  && apt-get update \
  && rosdep install --from-paths src --ignore-src -y \
  && colcon build \
  && rm -rf /var/lib/apt/lists/*

COPY vector-docker-ros2/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Le venv est créé au démarrage (car /root est un volume persistant).

# SDK configuration
#RUN python3 -m anki_vector.configure
# The SDK credentials are copied at runtime from /Vector/vector-wirepod-python-sdk/sdk_vector_config
# to /vector-wirepod-python-sdk/sdk_vector_config and then to ${ANKI_SDK_CONFIG_DIR}.

# Source ROS + overlay by default in interactive shells
RUN for BASHRC in /etc/bash.bashrc /root/.bashrc; do \
      echo "source /opt/ros/jazzy/setup.bash" >> "$BASHRC"; \
      echo "if [ -f ${WS}/install/setup.bash ]; then source ${WS}/install/setup.bash; fi" >> "$BASHRC"; \
      echo "if [ -f ${VENV_DIR}/bin/activate ]; then source ${VENV_DIR}/bin/activate; fi" >> "$BASHRC"; \
  echo "updatevectorip() { bash /Vector/vector-docker-ros2/scripts/updatevectorip.sh \"\$@\"; }" >> "$BASHRC"; \
    done && \
    printf '#!/usr/bin/env bash\nexec bash /Vector/vector-docker-ros2/scripts/updatevectorip.sh "$@"\n' > /usr/local/bin/updatevectorip && \
    chmod +x /usr/local/bin/updatevectorip

WORKDIR ${WS}

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]