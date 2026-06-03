#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"
#include "crb_ros_msg/srv/get_robot_mode.hpp"
#include "crb_ros_msg/srv/get_robot_state.hpp"
#include "crb_ros_msg/srv/set_robot_mode.hpp"

using namespace std::chrono_literals;

template<typename ServiceT>
bool wait_service(const rclcpp::Client<ServiceT>::SharedPtr &client, const std::string &name, rclcpp::Node &node)
{
  if (!client->wait_for_service(3s)) {
    RCLCPP_ERROR(node.get_logger(), "服务不可用: %s", name.c_str());
    return false;
  }
  return true;
}

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("service_mode_demo");

  auto get_mode = node->create_client<crb_ros_msg::srv::GetRobotMode>("get_robot_mode");
  auto set_mode = node->create_client<crb_ros_msg::srv::SetRobotMode>("/set_robot_mode");
  auto get_state = node->create_client<crb_ros_msg::srv::GetRobotState>("get_robot_state_srv_hl");
  auto switch_nav = node->create_client<std_srvs::srv::SetBool>("/motion/switch_nav_mode");
  auto switch_teleop = node->create_client<std_srvs::srv::SetBool>("/switch_teleoperation");
  auto switch_auto = node->create_client<std_srvs::srv::SetBool>("/switch_autonomous");

  if (!wait_service(get_mode, "get_robot_mode", *node) ||
      !wait_service(set_mode, "/set_robot_mode", *node) ||
      !wait_service(get_state, "get_robot_state_srv_hl", *node) ||
      !wait_service(switch_nav, "/motion/switch_nav_mode", *node) ||
      !wait_service(switch_teleop, "/switch_teleoperation", *node) ||
      !wait_service(switch_auto, "/switch_autonomous", *node)) {
    rclcpp::shutdown();
    return 1;
  }

  {
    auto req = std::make_shared<crb_ros_msg::srv::GetRobotMode::Request>();
    auto fut = get_mode->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, fut, 3s) == rclcpp::FutureReturnCode::SUCCESS) {
      const auto resp = fut.get();
      RCLCPP_INFO(node->get_logger(), "当前模式: mode=%d, mode_name=%s", resp->mode, resp->mode_name.c_str());
    }
  }

  {
    auto req = std::make_shared<crb_ros_msg::srv::GetRobotState::Request>();
    req->start = true;
    auto fut = get_state->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, fut, 3s) == rclcpp::FutureReturnCode::SUCCESS) {
      const auto resp = fut.get();
      RCLCPP_INFO(node->get_logger(), "机器人状态: state=%u", resp->state);
    }
  }

  {
    auto req = std::make_shared<crb_ros_msg::srv::SetRobotMode::Request>();
    req->mode_name = "WALK";
    auto fut = set_mode->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, fut, 3s) == rclcpp::FutureReturnCode::SUCCESS) {
      RCLCPP_INFO(node->get_logger(), "set_robot_mode(WALK): %s", fut.get()->success ? "success" : "failed");
    }
  }

  auto call_set_bool = [&node](const std::string &name, const rclcpp::Client<std_srvs::srv::SetBool>::SharedPtr &cli, bool data) {
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = data;
    auto fut = cli->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, fut, 3s) == rclcpp::FutureReturnCode::SUCCESS) {
      const auto resp = fut.get();
      RCLCPP_INFO(node->get_logger(), "%s(%s): success=%s, msg=%s",
        name.c_str(), data ? "true" : "false", resp->success ? "true" : "false", resp->message.c_str());
    }
  };

  call_set_bool("/motion/switch_nav_mode", switch_nav, true);
  call_set_bool("/motion/switch_nav_mode", switch_nav, false);
  call_set_bool("/switch_teleoperation", switch_teleop, true);
  call_set_bool("/switch_teleoperation", switch_teleop, false);
  call_set_bool("/switch_autonomous", switch_auto, true);
  call_set_bool("/switch_autonomous", switch_auto, false);

  rclcpp::shutdown();
  return 0;
}
