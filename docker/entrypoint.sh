#!/usr/bin/env bash
set -eo pipefail

WS="/ros_workspace"

# Raise the open-file limit when possible so Python/ROS startup does not fail with Errno 24.
if command -v ulimit >/dev/null 2>&1; then
    ulimit -n 65535 2>/dev/null || true
    echo "open files limit (nofile): $(ulimit -n)"
fi

source /opt/ros/jazzy/setup.bash

if [ -f "/Vector/vector-docker-ros2/scripts/updatevectorip.sh" ]; then
    if ! bash "/Vector/vector-docker-ros2/scripts/updatevectorip.sh"; then
        echo "Warning: updatevectorip failed during startup" >&2
    fi

    (
        while true; do
            sleep 600
            if ! bash "/Vector/vector-docker-ros2/scripts/updatevectorip.sh"; then
                echo "Warning: periodic updatevectorip failed" >&2
            fi
        done
    ) &
fi

# --- Copy SDK into the container filesystem and install it from there ---
if [ -d "/Vector/vector-wirepod-python-sdk" ]; then
    if [ ! -d "/vector-wirepod-python-sdk" ]; then
        cp -a "/Vector/vector-wirepod-python-sdk" "/vector-wirepod-python-sdk"
    fi
else
    echo "Warning: SDK python source not found at /Vector/vector-wirepod-python-sdk" >&2
fi

if [ -d "/vector-wirepod-python-sdk" ]; then
    if [ ! -d "/root/vector_ros2_venv" ]; then
        python3 -m venv --system-site-packages "/root/vector_ros2_venv"
    fi

    # shellcheck disable=SC1091
    source "/root/vector_ros2_venv/bin/activate"
    python3 -m pip install --upgrade pip
    PIP_USE_PEP517=0 python3 -m pip install --no-cache-dir -e "/vector-wirepod-python-sdk[3dviewer]"
    mkdir -p "${ANKI_SDK_CONFIG_DIR:-/root/sdk_vector_config}"
    if [ -d "/vector-wirepod-python-sdk/sdk_vector_config" ]; then
        cp -a "/vector-wirepod-python-sdk/sdk_vector_config/." "${ANKI_SDK_CONFIG_DIR:-/root/sdk_vector_config}/" || true
    fi
fi

cd "${WS}"

if [ ! -f "${WS}/install/setup.bash" ]; then
    echo "Error: ROS overlay not found at ${WS}/install/setup.bash (image build should have produced it)." >&2
    exit 1
fi

# shellcheck disable=SC1091
source "${WS}/install/setup.bash"

if [ "$#" -eq 0 ]; then
    set -- ros2 launch bringup manual_teleop.launch.py
fi

exec "$@"
