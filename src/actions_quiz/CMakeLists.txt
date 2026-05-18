cmake_minimum_required(VERSION 3.0.2)
project(ardrone_action_pkg)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  actionlib
  actionlib_msgs
  message_generation
)

add_action_files(
  DIRECTORY action
  FILES DroneCommand.action
)

generate_messages(
  DEPENDENCIES
  std_msgs
  actionlib_msgs
)

catkin_package(
  CATKIN_DEPENDS
  rospy
  std_msgs
  geometry_msgs
  actionlib
  actionlib_msgs
  message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  scripts/drone_action_server.py
  scripts/drone_action_client.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
