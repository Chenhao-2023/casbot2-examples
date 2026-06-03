// T02: 切换遥操作 / 自主模式
// 对应接口文档 switch_teleoperation / switch_autonomous
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/set_bool.hpp>

bool callSetBool(rclcpp::Node::SharedPtr node,
                 const std::string &srv_name, bool data,
                 const std::string &label)
{
    auto cli = node->create_client<std_srvs::srv::SetBool>(srv_name);
    RCLCPP_INFO(node->get_logger(), "[T02] 等待 %s ...", srv_name.c_str());
    if (!cli->wait_for_service(std::chrono::seconds(5))) {
        RCLCPP_ERROR(node->get_logger(), "[T02] %s 不可用", srv_name.c_str());
        return false;
    }
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = data;
    auto future = cli->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, future) == rclcpp::FutureReturnCode::SUCCESS) {
        auto resp = future.get();
        RCLCPP_INFO(node->get_logger(),
            "[T02] %s(%s) => success=%s  msg='%s'",
            label.c_str(), data ? "true" : "false",
            resp->success ? "true" : "false",
            resp->message.c_str());
        return resp->success;
    }
    RCLCPP_ERROR(node->get_logger(), "[T02] %s 调用失败", srv_name.c_str());
    return false;
}

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("t02_switch_mode");

    RCLCPP_INFO(node->get_logger(), "[T02] === 切换遥操作模式 ===");
    callSetBool(node, "/switch_teleoperation", true,  "switch_teleoperation");
    rclcpp::sleep_for(std::chrono::seconds(2));
    callSetBool(node, "/switch_teleoperation", false, "switch_teleoperation");
    rclcpp::sleep_for(std::chrono::seconds(1));

    RCLCPP_INFO(node->get_logger(), "[T02] === 切换自主（动作播放）模式 ===");
    callSetBool(node, "/switch_autonomous", true,  "switch_autonomous");
    rclcpp::sleep_for(std::chrono::seconds(2));
    callSetBool(node, "/switch_autonomous", false, "switch_autonomous");

    RCLCPP_INFO(node->get_logger(), "[T02] 完成");
    rclcpp::shutdown();
    return 0;
}
