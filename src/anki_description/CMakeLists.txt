cmake_minimum_required(VERSION 3.8)
project(anki_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    config
    doc
    gazebo_models
    launch
    meshes
    params
    proto
    urdf
    world
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
