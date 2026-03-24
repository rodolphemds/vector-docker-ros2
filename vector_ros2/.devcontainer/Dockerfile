FROM osrf/ros:kilted-desktop-full

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

ENV SHELL /bin/bash

# Create ROS log directory (owned by root)
RUN mkdir -p /root/.ros/log

CMD ["/bin/bash"]