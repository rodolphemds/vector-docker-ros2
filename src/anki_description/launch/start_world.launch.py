from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    put_robot_in_world = LaunchConfiguration("put_robot_in_world")
    gazebo_gui = LaunchConfiguration("gazebo_gui")

    gazebo_models_dir = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "gazebo_models"]
    )
    gz_sim_resource_path = [
        TextSubstitution(text="/opt/ros/jazzy/share:"),
        gazebo_models_dir,
        TextSubstitution(text=":/root/.gz/fuel"),
    ]

    gazebo_launch_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        condition=IfCondition(gazebo_gui),
        launch_arguments={
            "gz_args": [
                "-r -g ",
                PathJoinSubstitution(
                    [FindPackageShare("anki_description"), "world", "maze.world"]
                ),
            ],
        }.items(),
    )

    gazebo_launch_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        condition=UnlessCondition(gazebo_gui),
        launch_arguments={
            "gz_args": [
                "-r -s ",
                PathJoinSubstitution(
                    [FindPackageShare("anki_description"), "world", "maze.world"]
                ),
            ],
        }.items(),
    )

    put_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("anki_description"), "launch", "put_robot_in_world.launch.py"]
            )
        ),
        condition=IfCondition(put_robot_in_world),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("put_robot_in_world", default_value="false"),
            DeclareLaunchArgument("gazebo_gui", default_value="true"),
            SetEnvironmentVariable(name="GZ_SIM_RESOURCE_PATH", value=gz_sim_resource_path),
            SetEnvironmentVariable(name="GZ_SIM_MODEL_PATH", value=gazebo_models_dir),
            SetEnvironmentVariable(name="IGN_GAZEBO_RESOURCE_PATH", value=gz_sim_resource_path),
            gazebo_launch_gui,
            gazebo_launch_headless,
            put_robot,
        ]
    )
