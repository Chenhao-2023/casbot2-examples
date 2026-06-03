cmake_minimum_required(VERSION 3.8)
project(casbot2_cpp_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_srvs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(crb_ros_msg REQUIRED)

add_executable(basic_control_demo src/basic_control_demo.cpp)
ament_target_dependencies(
  basic_control_demo
  rclcpp
  std_srvs
  geometry_msgs
  crb_ros_msg
)

install(TARGETS basic_control_demo
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
