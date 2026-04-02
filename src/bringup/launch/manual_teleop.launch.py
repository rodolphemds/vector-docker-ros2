from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """
    Manual teleop launch for Vector robot — isolated testing (no Nav2).
    
    This launch file includes ONLY:
      - vector_controller_bringup: Vector driver and state publisher
      - foxglovebridge: foxglove_bridge for web-based visualization
    
    Purpose: Test Foxglove teleop without interference from Nav2 stack
    (collision_monitor, docking_server, velocity_smoother, etc.).
    
    Usage:
      ros2 launch bringup manual_teleop.launch.py
    
    Web visualization:
      - Foxglove Studio: https://studio.foxglove.dev (connect to ws://localhost:8765)
    
    To test teleop:
      1. Open Foxglove Studio and connect to ws://localhost:8765
      2. Add a Teleop panel (drag-and-drop) pointing to /cmd_vel
      3. Hold the arrow keys or drag the joystick sphere
      4. Observe robot movement and /camera/image_raw in parallel:
         - ros2 topic hz /cmd_vel
         - ros2 topic hz /camera/image_raw
    """

    vector_controller_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("bringup"), "launch", "vector_controller_bringup.launch.py"]
            )
        )
    )

    foxglovebridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("bringup"), "launch", "foxglovebridge.launch.py"]
            )
        )
    )

    return LaunchDescription(
        [
            vector_controller_bringup,
            foxglovebridge,
        ]
    )
