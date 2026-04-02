from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    ankirobot = LaunchConfiguration("ankirobot")

    model = PathJoinSubstitution(
        [FindPackageShare("anki_description"), "urdf", [ankirobot, ".xacro"]]
    )

    robot_description = {"robot_description": Command(["xacro ", model])}

    return LaunchDescription(
        [
            DeclareLaunchArgument("ankirobot", default_value="vector"),
            Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
                name="joint_state_publisher",
                output="screen",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[robot_description],
            ),
        ]
    )
