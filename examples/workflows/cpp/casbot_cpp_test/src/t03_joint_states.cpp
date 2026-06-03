// T03: 订阅关节状态反馈
// 对应接口文档 5.8 传感器数据订阅 / /joint_states
#include <rclcpp/rclcpp.hpp>
#include <thread>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/imu.hpp>

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("t03_joint_states");

    int joint_count = 0;
    int imu_count   = 0;

    // 订阅关节状态
    auto joint_sub = node->create_subscription<sensor_msgs::msg::JointState>(
        "/joint_states", 10,
        [&](const sensor_msgs::msg::JointState::SharedPtr msg) {
            ++joint_count;
            if (joint_count % 100 == 1) {  // 每 100 帧打印一次
                RCLCPP_INFO(node->get_logger(),
                    "[T03] /joint_states  joints=%zu  frame#%d",
                    msg->name.size(), joint_count);
                // 打印前 3 个关节
                for (size_t i = 0; i < std::min<size_t>(3, msg->name.size()); ++i) {
                    double pos = msg->position.size() > i ? msg->position[i] : 0.0;
                    double vel = msg->velocity.size() > i ? msg->velocity[i] : 0.0;
                    RCLCPP_INFO(node->get_logger(),
                        "[T03]   %-35s pos=%7.4f rad  vel=%7.4f rad/s",
                        msg->name[i].c_str(), pos, vel);
                }
            }
        });

    // 订阅 IMU
    auto imu_sub = node->create_subscription<sensor_msgs::msg::Imu>(
        "/imu", 10,
        [&](const sensor_msgs::msg::Imu::SharedPtr msg) {
            ++imu_count;
            if (imu_count % 200 == 1) {
                RCLCPP_INFO(node->get_logger(),
                    "[T03] /imu  orient w=%.3f x=%.3f y=%.3f z=%.3f  frame#%d",
                    msg->orientation.w, msg->orientation.x,
                    msg->orientation.y, msg->orientation.z, imu_count);
            }
        });

    RCLCPP_INFO(node->get_logger(), "[T03] 订阅 /joint_states 和 /imu，持续 5 秒...");
    auto deadline = node->now() + rclcpp::Duration(5, 0);
    while (rclcpp::ok() && node->now() < deadline) {
        rclcpp::spin_some(node);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    RCLCPP_INFO(node->get_logger(),
        "[T03] 完成：收到 joint_states %d 帧，imu %d 帧", joint_count, imu_count);
    rclcpp::shutdown();
    return 0;
}
