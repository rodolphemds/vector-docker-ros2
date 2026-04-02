from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, TextSubstitution
from launch.conditions import IfCondition, UnlessCondition
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    robot_type = LaunchConfiguration("robot_type")
    gazebo_gui = LaunchConfiguration("gazebo_gui")
    load_world = LaunchConfiguration("load_world")

    model = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "urdf", [robot_type, ".xacro"]]
    )
    robot_description = {"robot_description": Command(["xacro ", model])}

    world = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "world", "practice.world"]
    )

    # Ensure Gazebo can resolve model:// URIs.
    # practice.world references model://cafe_table and model://coke_can.
    # We ship a local model database under anki_description/gazebo_models.
    gz_fuel_cache_dir = "/root/.gz/fuel"
    gazebo_models_dir = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "gazebo_models"]
    )
    gz_sim_resource_path = [
        TextSubstitution(text="/opt/ros/jazzy/share:"),
        gazebo_models_dir,
        TextSubstitution(text=":" + gz_fuel_cache_dir),
    ]

    gazebo_launch_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        condition=IfCondition(gazebo_gui),
        launch_arguments={
            # -r: run, -g: gui
            "gz_args": ["-r -g ", world],
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
            "gz_args": ["-r ", world],
        }.items(),
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        name="urdf_spawner",
        output="screen",
        parameters=[{"topic": "robot_description", "name": "robot"}],
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"publish_frequency": 5.0}],
        remappings=[("/joint_states", ["/", robot_type, "/joint_states"])],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_type", default_value="vector"),
            DeclareLaunchArgument("gazebo_gui", default_value="true"),
            DeclareLaunchArgument("load_world", default_value="false"),
            SetEnvironmentVariable(name="GZ_SIM_RESOURCE_PATH", value=gz_sim_resource_path),
            SetEnvironmentVariable(name="GZ_SIM_MODEL_PATH", value=gazebo_models_dir),
            SetEnvironmentVariable(name="IGN_GAZEBO_RESOURCE_PATH", value=gz_sim_resource_path),
            gazebo_launch_gui,
            gazebo_launch_headless,
            robot_state_publisher,
            spawn,
        ]
    )
