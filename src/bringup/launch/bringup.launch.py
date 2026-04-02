from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """
    Bringup launch for Vector robot (complete system).
    
    This launch file includes:
      - vector_controller_bringup: Vector driver and state publisher
      - foxglovebridge: foxglove_bridge for web-based visualization
    
    Usage:
      ros2 launch bringup bringup.launch.py
    
    Web visualization:
            - Foxglove Studio: https://studio.foxglove.dev (connect to ws://localhost:8765)
    """


    vector_controller_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("bringup"), "launch", "vector_controller_bringup.launch.py"]
            )
        )
    )

    navigation_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("navigation"), "launch", "navigation.launch.py"]
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
            navigation_bringup,
            foxglovebridge,
        ]
    )

