#include <chrono>
#include <memory>
#include <thread>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("monitor_topics_demo");

  int joint_states_cnt = 0;
  int joint_control_cnt = 0;
  int imu_cnt = 0;
  int status_cnt = 0;
  int robot_state_cnt = 0;

  auto sub_joint_states = node->create_subscription<sensor_msgs::msg::JointState>(
    "/joint_states", 10, [&](const sensor_msgs::msg::JointState::SharedPtr) { joint_states_cnt++; });
  auto sub_joint_control = node->create_subscription<sensor_msgs::msg::JointState>(
    "/joint_control", 10, [&](const sensor_msgs::msg::JointState::SharedPtr) { joint_control_cnt++; });
  auto sub_imu = node->create_subscription<sensor_msgs::msg::Imu>(
    "/imu", 10, [&](const sensor_msgs::msg::Imu::SharedPtr) { imu_cnt++; });
  auto sub_status = node->create_subscription<std_msgs::msg::String>(
    "/motion/status", 10, [&](const std_msgs::msg::String::SharedPtr) { status_cnt++; });
  auto sub_robot_state = node->create_subscription<std_msgs::msg::String>(
    "/motion/robot_state", 10, [&](const std_msgs::msg::String::SharedPtr) { robot_state_cnt++; });

  (void)sub_joint_states;
  (void)sub_joint_control;
  (void)sub_imu;
  (void)sub_status;
  (void)sub_robot_state;

  RCLCPP_INFO(node->get_logger(), "开始监听 5 秒...");
  auto deadline = node->now() + rclcpp::Duration(5, 0);
  while (rclcpp::ok() && node->now() < deadline) {
    rclcpp::spin_some(node);
    std::this_thread::sleep_for(50ms);
  }

  RCLCPP_INFO(node->get_logger(), "/joint_states: %d", joint_states_cnt);
  RCLCPP_INFO(node->get_logger(), "/joint_control: %d", joint_control_cnt);
  RCLCPP_INFO(node->get_logger(), "/imu: %d", imu_cnt);
  RCLCPP_INFO(node->get_logger(), "/motion/status: %d", status_cnt);
  RCLCPP_INFO(node->get_logger(), "/motion/robot_state: %d", robot_state_cnt);

  rclcpp::shutdown();
  return 0;
}
