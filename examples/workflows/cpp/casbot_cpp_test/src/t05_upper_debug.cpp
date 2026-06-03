// T05: 进入/退出上身调试模式，并发布关节指令
// 对应接口文档 5.5 上身关节控制
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <crb_ros_msg/msg/upper_joint_data.hpp>

bool switchUpperBodyDebug(rclcpp::Node::SharedPtr node, bool enable)
{
    auto cli = node->create_client<std_srvs::srv::SetBool>("/motion/upper_body_debug");
    if (!cli->wait_for_service(std::chrono::seconds(5))) {
        RCLCPP_ERROR(node->get_logger(), "[T05] /motion/upper_body_debug 不可用");
        return false;
    }
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = enable;
    auto future = cli->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, future) == rclcpp::FutureReturnCode::SUCCESS) {
        auto resp = future.get();
        RCLCPP_INFO(node->get_logger(),
            "[T05] upper_body_debug(%s) => success=%s  msg='%s'",
            enable ? "true" : "false",
            resp->success ? "true" : "false",
            resp->message.c_str());
        return resp->success;
    }
    return false;
}

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("t05_upper_debug");

    // Step 1: 进入上身调试
    if (!switchUpperBodyDebug(node, true)) {
        RCLCPP_WARN(node->get_logger(), "[T05] 进入上身调试失败（可能当前模式不允许），继续观察...");
    }
    rclcpp::sleep_for(std::chrono::milliseconds(300));

    // Step 2: 以 10 Hz 发布上身关节指令，持续 2 秒（小角度 vel_scale=0.05 安全测试）
    auto pub = node->create_publisher<crb_ros_msg::msg::UpperJointData>(
        "/upper_body_debug/joint_cmd", 10);

    rclcpp::Rate rate(10);
    for (int i = 0; i < 20 && rclcpp::ok(); ++i) {
        crb_ros_msg::msg::UpperJointData msg;
        msg.header.stamp  = node->now();
        msg.header.frame_id = "base_link";
        msg.time_ref  = 0.0f;
        msg.vel_scale = 0.05f;  // 极低速度，安全测试
        msg.joint.name     = {"left_shoulder_pitch_joint", "right_shoulder_pitch_joint"};
        msg.joint.position = {0.05, 0.05};  // 5° 小幅度
        pub->publish(msg);
        if (i % 10 == 0) {
            RCLCPP_INFO(node->get_logger(),
                "[T05] 发布 joint_cmd vel_scale=%.2f  left_shoulder=%.3f rad  frame#%d",
                msg.vel_scale, msg.joint.position[0], i);
        }
        rclcpp::spin_some(node);
        rate.sleep();
    }

    // Step 3: 退出调试
    switchUpperBodyDebug(node, false);

    RCLCPP_INFO(node->get_logger(), "[T05] 完成");
    rclcpp::shutdown();
    return 0;
}
