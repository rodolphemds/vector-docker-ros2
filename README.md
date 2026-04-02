# controller

ROS 2 (Jazzy) wrapper for Anki Vector running OSKR + wire-pod.

## Repository Architecture

```text
vector-docker-ros2/
├── README.md
├── anim_list.md
├── docker/
├── dockerfile
├── scripts/
└── src/
```

- `README.md`: overview, topics/services, parameters, and container notes.
- `anim_list.md`: reference list of animation names usable via the ROS2 service.
- `docker/`: container runtime assets (including `entrypoint.sh`).
- `dockerfile`: image build recipe for the ROS2 Jazzy + SDK runtime.
- `scripts/`: helper scripts (for example IP update logic).
- `src/`: ROS 2 packages (`anki_description`, `vector_controller`, `bringup`).

At runtime, the ROS overlay workspace lives in `/ros_workspace` (it is not under the `/root` volume).

## SDK Configuration File Locations

- Host workspace source: `vector-wirepod-python-sdk/sdk_vector_config`
- Container copied source: `/vector-wirepod-python-sdk/sdk_vector_config`
- Container runtime target (used by SDK): `/root/sdk_vector_config`
- Runtime override env var: `ANKI_SDK_CONFIG_DIR`

At container startup, `docker/entrypoint.sh` copies the SDK repo from `/Vector/vector-wirepod-python-sdk` to `/vector-wirepod-python-sdk`, then copies `sdk_vector_config` into the runtime target.

## What it does

Publishes:
- `pose` (geometry_msgs/PoseStamped)
- `odom` (nav_msgs/Odometry)
- `imu` (sensor_msgs/Imu)
- `battery` (sensor_msgs/BatteryState)
- `proximity/range` (sensor_msgs/Range)
- `touch` (std_msgs/Bool)
- `touch/raw` (std_msgs/Float32)
- `cliff_detected` (std_msgs/Bool)
- `joint_states` (sensor_msgs/JointState) for head and lift (URDF joint names)
- `nav_map` (nav_msgs/OccupancyGrid)
- `camera/image_raw` (sensor_msgs/Image)
- `camera/camera_info` (sensor_msgs/CameraInfo)

Subscribes:
- `cmd_vel` (geometry_msgs/Twist)
- `head_angle_cmd` (std_msgs/Float32)
- `lift_height_cmd` (std_msgs/Float32)

Services:
- `start_exploration` (std_srvs/Trigger)
- `fetch_cube` (std_srvs/Trigger)
- `go_home` (std_srvs/Trigger)
- `drive_off_charger` (std_srvs/Trigger)
- `play_animation` (vector_controller/srv/PlayAnimationTrigger)
- `say_text` (vector_controller/srv/SayText)

## Installation
 


## Notes

- `cmd_vel` is converted to wheel speeds using `wheel_track_mm`. Tune if turning feels off.
- `max_wheel_speed_mmps` limits wheel speed (set to 0 to disable limit).
- `head_angle_cmd` is radians.
- `lift_height` topic is meters. `lift_height_cmd` is also meters; the driver maps it to the SDK’s
  normalized 0.0–1.0 range using `lift_height_min_m`/`lift_height_max_m`.
- IMU values are scaled by `imu_accel_scale` and `imu_gyro_scale` before publishing.
- If you use a venv for the SDK, set `venv_site_packages` in the launch file or export
  `VECTOR_VENV_SITE_PACKAGES` to point at the venv site-packages. The launch file
  appends this to `PYTHONPATH` so ROS 2 can still find the package metadata.
- The Vector URDF/xacro and meshes come from `anki_description` and are launched with
  `robot_state_publisher` by default.
- For Foxglove 3D mesh rendering, use `foxglove_bridge`.
- This version of vector-docker-ros2 uses the rodolphemds/vector-wirepod-python-sdk version. Credentials are stored in `vector-wirepod-python-sdk/sdk_vector_config` and copied to `/root/sdk_vector_config` at runtime. This avoids rerunning `anki_vector.configure` inside the container.

## Foxglove 3D Mesh Fix

If Foxglove shows errors like `Failed to load asset package://anki_description/meshes/...`, install and use `foxglove_bridge`:

```bash
sudo apt update
sudo apt install -y ros-jazzy-foxglove-bridge
ros2 launch bringup bringup.launch.py
```

Then connect Foxglove Studio to:

```text
ws://<your-host>:8765
```

Fallback (temporary): if you cannot use `foxglove_bridge` immediately, you can disable meshes:

```bash
ros2 launch vector_controller vector.launch.py use_meshes:=false
```

## Parameters

- `serial` (string): optional Vector serial (recommended if you have multiple)
- `ip` (string): optional Vector IP
- `state_hz` (float): publish rate for pose/imu/etc
- `battery_hz` (float): publish rate for battery
- `camera_hz` (float): publish rate for camera
- `cmd_vel_timeout_sec` (float): stop motors if no cmd_vel for this duration
- `nav_map_hz` (float): publish rate for nav map
- `nav_map_resolution_m` (float): nav map grid resolution (meters)
- `control_release_timeout_sec` (float): release control after cmd_vel timeout (seconds)
- `behavior_control_level` (string): `default`, `override`, `reserve`, or `none` (default `override`)
  - `default`: DEFAULT_PRIORITY (above mandatory physical reactions, below trigger‑word detection)
  - `override`: OVERRIDE_BEHAVIORS_PRIORITY (above mandatory physical reactions and trigger‑word detection)
  - `reserve`: RESERVE_CONTROL (holds control before/after other SDK connections; disables idle behaviors)
  - `none`: do not hold control by default; driver requests control only when needed
- `hold_control_during_cmd_vel` (bool): keep control while cmd_vel is active
- `always_hold_control` (bool): hold control continuously (prevents idle roaming)
- `enable_camera` (bool)
- `enable_face_detection` (bool)
- `enable_nav_map_feed` (bool)
- `enable_custom_object_detection` (bool)
- `enable_audio_feed` (bool)
- `frame_odom` (string)
- `frame_base` (string)
- `frame_footprint` (string): child frame for odom/TF (default `base_footprint`)
- `wheel_track_mm` (float)
- `max_wheel_speed_mmps` (float)
- `publish_tf` (bool): publish `odom` → `base_link` transform
- `use_robot_state_publisher` (bool): launch `robot_state_publisher` (default true)
- `model` (string): path to the xacro model (default anki_description/urdf/vector.xacro)
- `joint_head_name` (string): URDF joint for head (default `base_to_head`)
- `joint_lift_name` (string): URDF joint for lift (default `base_to_lift`)
- `lift_use_angle` (bool): use SDK `lift_angle_rad` if available
- `lift_height_to_angle_scale` (float): scale meters → radians when lift angle isn't available
- `lift_height_to_angle_offset` (float): offset radians when lift angle isn't available
- `lift_height_min_m` (float): minimum lift height (meters) for command mapping (default 0.032)
- `lift_height_max_m` (float): maximum lift height (meters) for command mapping (default 0.09)
- `imu_accel_scale` (float): multiply accel values from SDK (default 0.001 to convert mm/s^2 → m/s^2)
- `imu_gyro_scale` (float): multiply gyro values from SDK (default 1.0)
- `head_angle_scale` (float): scale head angle from SDK before publishing joint state
- `head_angle_offset` (float): offset head angle (radians) before publishing joint state

## Services

`play_animation` expects an animation trigger name:

```bash
ros2 service call /play_animation vector_controller/srv/PlayAnimationTrigger "{name: GreetAfterLongTime}"
```

List available animation triggers via the SDK:

```bash
python - <<'PY'
import anki_vector

with anki_vector.Robot() as robot:
    for name in robot.anim.anim_trigger_list:
        print(name)
PY
```

## Next steps

- Add face/object detection topics.
- Add audio input/output topics.
- Publish TF tree.
- Add diagnostics for SDK connection state.

## Dev Container

### Aim 
The aim is to create a stack of containers : 
- ros2-jazzy-desktop : the core ROS2 Jazzy Desktop 
- novnc-display-server : the graphical user interface for ROS2 accessible through a web browser 
- vector-ros2 : the container for ROS2 Vector's specific package 
- ros2-packages : the container for ROS2 other packages (TO DO) 
This stack of containers integrates in the existing EscapePod one and is orchestrated with OrbStack. 

### Content 
TO GENERATE 




### Notes
- novnc-display-server container relies on rodolphemds/docker-noVNC-display GitHub package stored on my computer at /Users/rodolphe/Documents/Docker/docker-noVNC-display. You can change this in .devcontainer/Dockerfile 
- vector-ros2 container relies on rodolphemds/vector-docker-ros2 GitHub package stored on my computer at /Users/rodolphe/Documents/Docker/docker-noVNC-display. You can change this in .devcontainer/Dockerfile  /Users/rodolphe/Documents/Vector/vector-docker-ros2/