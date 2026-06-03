// T04: 发布行走速度指令（cmd_vel）
// 对应接口文档 5.4 下肢行走控制
// 注意：仿真中机器人须处于 NAVIGATION 模式指令才生效
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("t04_cmd_vel");

    auto pub = node->create_publisher<geometry_msgs::msg::Twist>(
        "/navigation/cmd_vel", 10);

    RCLCPP_INFO(node->get_logger(),
        "[T04] 开始发布 /navigation/cmd_vel（机器人须在 NAVIGATION 模式下才有效）");

    // 以 10 Hz 发布前进 0.3 m/s，持续 3 秒
    rclcpp::Rate rate(10);
    int frames = 0;
    while (rclcpp::ok() && frames < 30) {
        geometry_msgs::msg::Twist msg;
        msg.linear.x  = 0.3;
        msg.angular.z = 0.0;
        pub->publish(msg);
        ++frames;
        if (frames % 10 == 1) {
            RCLCPP_INFO(node->get_logger(),
                "[T04] 发布 vx=%.2f wz=%.2f  frame#%d", msg.linear.x, msg.angular.z, frames);
        }
        rclcpp::spin_some(node);
        rate.sleep();
    }

    // 发送停止指令
    geometry_msgs::msg::Twist stop;
    stop.linear.x  = 0.0;
    stop.angular.z = 0.0;
    pub->publish(stop);
    rclcpp::spin_some(node);
    RCLCPP_INFO(node->get_logger(), "[T04] 停止指令已发送");

    RCLCPP_INFO(node->get_logger(), "[T04] 完成");
    rclcpp::shutdown();
    return 0;
}
