from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """
    Launch the Vector controller node.
    
    This launch file includes vector.launch.py from the vector_controller package,
    which starts the vector_driver and robot_state_publisher nodes.
    
    Usage:
      ros2 launch bringup vector_controller_bringup.launch.py
    """
    
    vector = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("vector_controller"), "launch", "vector.launch.py"]
            )
        )
    )

    return LaunchDescription([vector])
