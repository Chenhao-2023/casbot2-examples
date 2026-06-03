#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"
#include "crb_ros_msg/msg/joint_state_data.hpp"
#include "crb_ros_msg/msg/upper_joint_data.hpp"

using namespace std::chrono_literals;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("debug_joint_demo");

  auto upper_dbg_cli = node->create_client<std_srvs::srv::SetBool>("/motion/upper_body_debug");
  auto whole_dbg_cli = node->create_client<std_srvs::srv::SetBool>("/motion/whole_body_debug");
  auto upper_pub = node->create_publisher<crb_ros_msg::msg::UpperJointData>("/upper_body_debug/joint_cmd", 10);
  auto whole_pub = node->create_publisher<crb_ros_msg::msg::JointStateData>("/motion/joint_cmd", 10);

  if (!upper_dbg_cli->wait_for_service(3s) || !whole_dbg_cli->wait_for_service(3s)) {
    RCLCPP_ERROR(node->get_logger(), "Debug 服务不可用");
    rclcpp::shutdown();
    return 1;
  }

  {
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = true;
    auto fut = upper_dbg_cli->async_send_request(req);
    rclcpp::spin_until_future_complete(node, fut, 3s);
  }

  {
    crb_ros_msg::msg::UpperJointData msg;
    msg.header.stamp = node->now();
    msg.vel_scale = 0.05f;
    msg.time_ref = 0.0f;
    msg.joint.name = {"left_shoulder_pitch_joint", "right_shoulder_pitch_joint"};
    msg.joint.position = {0.05, 0.05};
    msg.joint.velocity = {0.0, 0.0};
    msg.joint.effort = {0.0, 0.0};
    upper_pub->publish(msg);
    RCLCPP_INFO(node->get_logger(), "已发送 upper_body_debug 关节命令");
  }

  {
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = false;
    auto fut = upper_dbg_cli->async_send_request(req);
    rclcpp::spin_until_future_complete(node, fut, 3s);
  }

  {
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = true;
    auto fut = whole_dbg_cli->async_send_request(req);
    rclcpp::spin_until_future_complete(node, fut, 3s);
  }

  {
    crb_ros_msg::msg::JointStateData msg;
    msg.header.stamp = node->now();
    msg.name = {"head_yaw_joint", "head_pitch_joint", "waist_yaw_joint"};
    msg.position = {0.1, -0.05, 0.0};
    msg.velocity = {0.0, 0.0, 0.0};
    msg.effort = {0.0, 0.0, 0.0};
    msg.kp = {};
    msg.kd = {};
    whole_pub->publish(msg);
    RCLCPP_INFO(node->get_logger(), "已发送 whole_body_debug 关节命令");
  }

  {
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = false;
    auto fut = whole_dbg_cli->async_send_request(req);
    rclcpp::spin_until_future_complete(node, fut, 3s);
  }

  rclcpp::shutdown();
  return 0;
}
