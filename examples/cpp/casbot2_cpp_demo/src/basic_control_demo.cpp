#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"
#include "crb_ros_msg/msg/joint_state_data.hpp"

using namespace std::chrono_literals;

class BasicControlDemo : public rclcpp::Node
{
public:
  BasicControlDemo() : Node("casbot2_basic_control_demo")
  {
    nav_mode_cli_ = create_client<std_srvs::srv::SetBool>("/motion/switch_nav_mode");
    cmd_vel_pub_ = create_publisher<geometry_msgs::msg::Twist>("/navigation/cmd_vel", 10);
    whole_body_pub_ = create_publisher<crb_ros_msg::msg::JointStateData>("/motion/joint_cmd", 10);
  }

  bool switch_nav_mode(bool enable_nav)
  {
    if (!nav_mode_cli_->wait_for_service(3s)) {
      RCLCPP_ERROR(get_logger(), "Service /motion/switch_nav_mode not available");
      return false;
    }
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = enable_nav;
    auto future = nav_mode_cli_->async_send_request(req);
    if (rclcpp::spin_until_future_complete(shared_from_this(), future, 3s) !=
      rclcpp::FutureReturnCode::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "Failed to call /motion/switch_nav_mode");
      return false;
    }
    const auto resp = future.get();
    RCLCPP_INFO(get_logger(), "switch_nav_mode(%s): success=%s, msg=%s",
      enable_nav ? "NAVIGATION" : "IDLE_MODE",
      resp->success ? "true" : "false",
      resp->message.c_str());
    return resp->success;
  }

  void send_cmd_vel(double vx, double wz)
  {
    geometry_msgs::msg::Twist msg;
    msg.linear.x = vx;
    msg.angular.z = wz;
    cmd_vel_pub_->publish(msg);
  }

  void send_whole_body_demo()
  {
    crb_ros_msg::msg::JointStateData msg;
    msg.header.stamp = now();
    msg.name = {"head_yaw_joint", "head_pitch_joint", "waist_yaw_joint"};
    msg.position = {0.1, -0.05, 0.0};
    msg.velocity = {0.0, 0.0, 0.0};
    msg.effort = {0.0, 0.0, 0.0};
    msg.kp = {};
    msg.kd = {};
    whole_body_pub_->publish(msg);
  }

private:
  rclcpp::Client<std_srvs::srv::SetBool>::SharedPtr nav_mode_cli_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
  rclcpp::Publisher<crb_ros_msg::msg::JointStateData>::SharedPtr whole_body_pub_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<BasicControlDemo>();

  node->switch_nav_mode(true);
  rclcpp::Rate rate(10.0);
  for (int i = 0; i < 20 && rclcpp::ok(); ++i) {
    node->send_cmd_vel(0.2, 0.0);
    rclcpp::spin_some(node);
    rate.sleep();
  }
  node->switch_nav_mode(false);

  node->send_whole_body_demo();
  rclcpp::spin_some(node);

  rclcpp::shutdown();
  return 0;
}
