from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    ankirobot = LaunchConfiguration("ankirobot")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    z = LaunchConfiguration("z")
    roll = LaunchConfiguration("roll")
    pitch = LaunchConfiguration("pitch")
    yaw = LaunchConfiguration("yaw")

    model = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "urdf", [ankirobot, ".xacro"]]
    )

    robot_description = {"robot_description": Command(["xacro ", model])}

    return LaunchDescription(
        [
            DeclareLaunchArgument("ankirobot", default_value="vector"),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("z", default_value="0.0"),
            DeclareLaunchArgument("roll", default_value="0.0"),
            DeclareLaunchArgument("pitch", default_value="0.0"),
            DeclareLaunchArgument("yaw", default_value="0.0"),
            Node(
                package="ros_gz_sim",
                executable="create",
                name="spawn_model",
                output="screen",
                parameters=[
                    {
                        "topic": "robot_description",
                        "name": "vector",
                        "allow_renaming": False,
                        "x": x,
                        "y": y,
                        "z": z,
                        "R": roll,
                        "P": pitch,
                        "Y": yaw,
                    }
                ],
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[robot_description, {"publish_frequency": 5.0}],
            ),
        ]
    )
