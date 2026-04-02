from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    default_map = PathJoinSubstitution(
        [FindPackageShare("navigation"), "maps", "vector_map.yaml"]
    )

    map_arg = DeclareLaunchArgument(
        "map",
        default_value=default_map,
        description="Absolute path to map yaml file",
    )

    autostart_arg = DeclareLaunchArgument(
        "autostart",
        default_value="True",
        description="Autostart Nav2 stack",
    )

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("nav2_bringup"), "launch", "bringup_launch.py"]
            )
        ),
        launch_arguments={
            "autostart": LaunchConfiguration("autostart"),
            "map": LaunchConfiguration("map"),
        }.items(),
    )

    vector_controller = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("vector_controller"), "launch", "vector.launch.py"]
            )
        )
    )

    return LaunchDescription([
        map_arg,
        autostart_arg,
        vector_controller,
        nav2_bringup,
    ])
