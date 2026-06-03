// T01: 查询机器人运控状态
// 对应接口文档 5.3 获取机器人状态
#include <rclcpp/rclcpp.hpp>
#include <thread>
#include <crb_ros_msg/srv/get_robot_state.hpp>
#include <std_msgs/msg/string.hpp>

static const std::map<int, std::string> STATE_MAP = {
    {0, "UNDEFINED"},
    {1, "DAMPING"},
    {2, "READY"},
    {3, "STAND"},
    {4, "WALKING"},
    {5, "RUNNING"},
    {255, "EMERGENCY_STOP"},
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("t01_get_state");

    // --- 1. 通过 Service 查询状态 ---
    auto client = node->create_client<crb_ros_msg::srv::GetRobotState>("get_robot_state_srv_hl");
    RCLCPP_INFO(node->get_logger(), "[T01] 等待 /get_robot_state 服务...");
    if (!client->wait_for_service(std::chrono::seconds(5))) {
        RCLCPP_ERROR(node->get_logger(), "[T01] 服务不可用，超时退出");
        rclcpp::shutdown();
        return 1;
    }

    auto req = std::make_shared<crb_ros_msg::srv::GetRobotState::Request>();
    req->start = true;
    auto future = client->async_send_request(req);

    if (rclcpp::spin_until_future_complete(node, future) == rclcpp::FutureReturnCode::SUCCESS) {
        int state = static_cast<int>(future.get()->state);
        auto it = STATE_MAP.find(state);
        std::string name = (it != STATE_MAP.end()) ? it->second : "UNKNOWN";
        RCLCPP_INFO(node->get_logger(),
            "[T01] GetRobotState => state=%d (%s)", state, name.c_str());
    } else {
        RCLCPP_ERROR(node->get_logger(), "[T01] Service 调用失败");
    }

    // --- 2. 通过 Topic 订阅状态字符串 ---
    RCLCPP_INFO(node->get_logger(), "[T01] 订阅 /motion/status (3 秒)...");
    std::string last_status;
    auto sub = node->create_subscription<std_msgs::msg::String>(
        "/motion/status", 10,
        [&last_status, &node](const std_msgs::msg::String::SharedPtr msg) {
            if (last_status != msg->data) {
                last_status = msg->data;
                RCLCPP_INFO(node->get_logger(), "[T01] /motion/status: %s", msg->data.c_str());
            }
        });

    auto deadline = node->now() + rclcpp::Duration(3, 0);
    while (rclcpp::ok() && node->now() < deadline) {
        rclcpp::spin_some(node);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    RCLCPP_INFO(node->get_logger(), "[T01] 完成");
    rclcpp::shutdown();
    return 0;
}
