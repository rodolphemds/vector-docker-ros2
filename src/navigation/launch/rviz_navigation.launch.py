from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("nav2_bringup"), "rviz", "nav2_default_view.rviz"]
    )

    vector_controller = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("vector_controller"), "launch", "vector.launch.py"]
            )
        )
    )

    return LaunchDescription(
        [
            vector_controller,
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2_navigation",
                output="screen",
                arguments=["-d", rviz_config],
            )
        ]
    )
