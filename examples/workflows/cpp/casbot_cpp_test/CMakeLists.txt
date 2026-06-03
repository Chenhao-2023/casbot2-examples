cmake_minimum_required(VERSION 3.16)
project(casbot_cpp_test)

set(CMAKE_CXX_STANDARD 17)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_srvs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(crb_ros_msg REQUIRED)

set(DEPS
  rclcpp
  rclcpp_action
  std_srvs
  std_msgs
  geometry_msgs
  sensor_msgs
  crb_ros_msg
)

# T01: 查询机器人状态
add_executable(t01_get_state src/t01_get_state.cpp)
ament_target_dependencies(t01_get_state ${DEPS})

# T02: 切换遥操作/自主模式
add_executable(t02_switch_mode src/t02_switch_mode.cpp)
ament_target_dependencies(t02_switch_mode ${DEPS})

# T03: 订阅关节状态
add_executable(t03_joint_states src/t03_joint_states.cpp)
ament_target_dependencies(t03_joint_states ${DEPS})

# T04: 发布行走速度
add_executable(t04_cmd_vel src/t04_cmd_vel.cpp)
ament_target_dependencies(t04_cmd_vel ${DEPS})

# T05: 进入/退出上身调试
add_executable(t05_upper_debug src/t05_upper_debug.cpp)
ament_target_dependencies(t05_upper_debug ${DEPS})

install(TARGETS
  t01_get_state
  t02_switch_mode
  t03_joint_states
  t04_cmd_vel
  t05_upper_debug
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
