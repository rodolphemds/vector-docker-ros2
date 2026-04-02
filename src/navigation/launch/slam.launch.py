from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    vector_controller = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("vector_controller"), "launch", "vector.launch.py"]
            )
        )
    )

    nav2_navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("nav2_bringup"), "launch", "navigation_launch.py"]
            )
        )
    )

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam_toolbox"), "launch", "online_async_launch.py"]
            )
        )
    )

    hint = LogInfo(
        msg=(
            "Move your robot by requesting a goal through RViz or the ROS 2 CLI. "
            "You should see the map update live. To save this map to file, run : "
            "ros2 run nav2_map_server map_saver_cli -f "
            "/Vector/vector-docker-ros2/src/navigation/maps/your-map-name.yaml"
        )
    )

    return LaunchDescription([
        vector_controller,
        nav2_navigation,
        slam_toolbox,
        hint,
    ])
