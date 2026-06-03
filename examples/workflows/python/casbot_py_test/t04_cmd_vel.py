#!/usr/bin/env python3
"""T04: 发布行走速度指令 — 对应接口文档 5.4 下肢行走控制"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

def main():
    rclpy.init()
    node = Node('t04_cmd_vel_py')
    pub = node.create_publisher(Twist, '/navigation/cmd_vel', 10)

    node.get_logger().info(
        '[T04] 开始发布 /navigation/cmd_vel（机器人须在 NAVIGATION 模式下才有效）')

    # 10 Hz 前进 0.3 m/s，持续 3 秒
    rate = node.create_rate(10)
    for i in range(30):
        if not rclpy.ok(): break
        msg = Twist()
        msg.linear.x  = 0.3
        msg.angular.z = 0.0
        pub.publish(msg)
        if i % 10 == 0:
            node.get_logger().info(
                f'[T04] 发布 vx={msg.linear.x:.2f} wz={msg.angular.z:.2f}  frame#{i+1}')
        rclpy.spin_once(node, timeout_sec=0.05)
        rate.sleep()

    # 停止
    stop = Twist()
    pub.publish(stop)
    rclpy.spin_once(node, timeout_sec=0.1)
    node.get_logger().info('[T04] 停止指令已发送')
    node.get_logger().info('[T04] 完成')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
