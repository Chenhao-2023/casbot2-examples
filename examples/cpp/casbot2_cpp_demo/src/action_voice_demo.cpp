#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "crb_ros_msg/action/basic_action_play.hpp"
#include "crb_ros_msg/action/voice_play.hpp"
#include "crb_ros_msg/srv/action_event.hpp"
#include "crb_ros_msg/srv/voice.hpp"

using BasicActionPlay = crb_ros_msg::action::BasicActionPlay;
using VoicePlay = crb_ros_msg::action::VoicePlay;
using namespace std::chrono_literals;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("action_voice_demo");

  auto event_cli = node->create_client<crb_ros_msg::srv::ActionEvent>("/casbot/event_service");
  auto voice_cli = node->create_client<crb_ros_msg::srv::Voice>("/voice_svr");
  auto basic_action_cli = rclcpp_action::create_client<BasicActionPlay>(node, "/basic_action_play");
  auto voice_action_cli = rclcpp_action::create_client<VoicePlay>(node, "/action_voice_play");

  if (event_cli->wait_for_service(2s)) {
    auto req = std::make_shared<crb_ros_msg::srv::ActionEvent::Request>();
    req->event_id = "";
    req->event_type = "ExecSkill";
    req->blocking = false;
    req->param_json = "{\"payload\":\"{\\\"action_type\\\":\\\"wave_hand\\\"}\",\"target_tree\":\"basic_action_play\"}";
    auto fut = event_cli->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, fut, 3s) == rclcpp::FutureReturnCode::SUCCESS) {
      RCLCPP_INFO(node->get_logger(), "event_service: success=%s msg=%s",
        fut.get()->success ? "true" : "false", fut.get()->message.c_str());
    }
  }

  if (voice_cli->wait_for_service(2s)) {
    auto req = std::make_shared<crb_ros_msg::srv::Voice::Request>();
    req->type = "question";
    req->content_type = "text";
    req->content = "你好";
    auto fut = voice_cli->async_send_request(req);
    rclcpp::spin_until_future_complete(node, fut, 3s);
    if (fut.valid() && fut.wait_for(0s) == std::future_status::ready) {
      RCLCPP_INFO(node->get_logger(), "voice_svr: success=%s", fut.get()->success ? "true" : "false");
    }
  }

  if (basic_action_cli->wait_for_action_server(2s)) {
    BasicActionPlay::Goal goal;
    goal.type = "wave_hand";
    auto send_future = basic_action_cli->async_send_goal(goal);
    rclcpp::spin_until_future_complete(node, send_future, 3s);
    RCLCPP_INFO(node->get_logger(), "basic_action_play goal sent");
  }

  if (voice_action_cli->wait_for_action_server(2s)) {
    VoicePlay::Goal goal;
    goal.wav_path = "test.wav";
    auto send_future = voice_action_cli->async_send_goal(goal);
    rclcpp::spin_until_future_complete(node, send_future, 3s);
    RCLCPP_INFO(node->get_logger(), "voice_play goal sent");
  }

  rclcpp::shutdown();
  return 0;
}
