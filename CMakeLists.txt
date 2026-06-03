cmake_minimum_required(VERSION 3.8)
project(crb_ros_msg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)


set(msg_files
  "msg/UpperJointData.msg"
  "msg/HlArmState.msg"
  "msg/ArmState.msg"
  "msg/LegState.msg"
  "msg/RobotState.msg"
  "msg/WholeBodyState.msg"
  "msg/DexterousHandState.msg"
  "msg/HeadState.msg"
  "msg/FaultRecord.msg"
  "msg/FaultSnapshot.msg"
  "msg/JoystickCmdReport.msg"
  "msg/NodeStatus.msg"
)

set(srv_files
  "srv/GetRobotState.srv"
  "srv/Voice.srv"
  "srv/GetRobotMode.srv"
  "srv/ActionEvent.srv"
  "srv/SetRobotMode.srv"
  "srv/SwitchMode.srv"
)

set(action_files
  "action/ActionPlay.action"
  "action/BasicActionPlay.action"
  "action/ActionPlayerReset.action"
  "action/LogOutData.action"
  "action/ExecuteTree.action"
  "action/Sleep.action"
)

# 生成消息接口
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  ${action_files}
  DEPENDENCIES std_msgs sensor_msgs
)

# Export include directories
ament_export_include_directories(include)

ament_export_dependencies(
  std_msgs
  sensor_msgs
  rosidl_default_runtime
)


ament_package()
