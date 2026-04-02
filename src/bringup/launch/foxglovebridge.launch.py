from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """
        Launch Foxglove Bridge for web-based visualization.

        This launch file exposes ROS 2 topics and assets over WebSocket.
    
    Usage:
            ros2 launch bringup foxglovebridge.launch.py
    
        Web visualization:
            Foxglove Studio: https://studio.foxglove.dev
            Connect to: ws://localhost:8765
    """

    foxglove_port = LaunchConfiguration("foxglove_port")

    foxglove_node = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
        output="screen",
        parameters=[
            {"port": foxglove_port},
            {
                "asset_uri_allowlist": [
                    "package://.*",
                    "file://.*",
                ]
            },
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "foxglove_port",
                default_value="8765",
                description="Port for foxglove_bridge server",
            ),
            foxglove_node,
        ]
    )

