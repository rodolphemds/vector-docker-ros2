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

# --- Workspace layout (README uses /home/nils/vector_ws) ---
ARG USERNAME=devuser
ENV HOME=/home/${USERNAME}
ENV WS=${HOME}/vector_ws
ENV VENV_DIR=${WS}/.vector

RUN useradd -m -s /bin/bash ${USERNAME}
WORKDIR ${WS}

# Copy repository into the container workspace
# Assumes the repo content is the build context.
COPY --chown=${USERNAME}:${USERNAME} . ${WS}/src/vector_ros2

# Récupérer le SDK depuis GitHub et l'installer
RUN git clone --depth 1 https://github.com/rodolphemds/vector-wirepod-python-sdk.git /opt/vector-wirepod-python-sdk && \
    python3 -m pip install --break-system-packages --no-cache-dir /opt/vector-wirepod-python-sdk && \
    rm -rf /opt/vector-wirepod-python-sdk
# Configurer le SDK 
RUN python3 -m anki_vector.configure

RUN set -eux; \
    python3 -m venv --system-site-packages "${VENV_DIR}"; \
    source "${VENV_DIR}/bin/activate"; \
    python3 -m pip install --upgrade pip; \
    source /opt/ros/jazzy/setup.bash; \
    colcon build --packages-select vector_ros2

# Source ROS + overlay by default in interactive shells
RUN echo "source /opt/ros/jazzy/setup.bash" >> /etc/bash.bashrc && \
    echo "source ${WS}/install/setup.bash" >> /etc/bash.bashrc && \
    echo "source ${VENV_DIR}/bin/activate" >> /etc/bash.bashrc


# We keep it as a runtime step.
USER ${USERNAME}
WORKDIR ${WS}

CMD ["ros2 launch vector_ros2 vector.launch.py"]