cmake_minimum_required(VERSION 3.8)
project(casbot2_cpp_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_srvs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(crb_ros_msg REQUIRED)

add_executable(basic_control_demo src/basic_control_demo.cpp)
ament_target_dependencies(
  basic_control_demo
  rclcpp
  rclcpp_action
  std_srvs
  std_msgs
  geometry_msgs
  sensor_msgs
  crb_ros_msg
)

add_executable(service_mode_demo src/service_mode_demo.cpp)
ament_target_dependencies(
  service_mode_demo
  rclcpp
  std_srvs
  crb_ros_msg
)

add_executable(debug_joint_demo src/debug_joint_demo.cpp)
ament_target_dependencies(
  debug_joint_demo
  rclcpp
  std_srvs
  std_msgs
  sensor_msgs
  crb_ros_msg
)

add_executable(monitor_topics_demo src/monitor_topics_demo.cpp)
ament_target_dependencies(
  monitor_topics_demo
  rclcpp
  std_msgs
  sensor_msgs
  crb_ros_msg
)

add_executable(action_voice_demo src/action_voice_demo.cpp)
ament_target_dependencies(
  action_voice_demo
  rclcpp
  rclcpp_action
  std_srvs
  crb_ros_msg
)

install(TARGETS
  basic_control_demo
  service_mode_demo
  debug_joint_demo
  monitor_topics_demo
  action_voice_demo
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
