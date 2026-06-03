#!/usr/bin/env python3
"""T05: 进入/退出上身调试模式，发布关节指令 — 对应接口文档 5.5"""
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.msg import UpperJointData
import time

def switch_debug(node: Node, enable: bool) -> bool:
    cli = node.create_client(SetBool, '/motion/upper_body_debug')
    if not cli.wait_for_service(timeout_sec=5.0):
        node.get_logger().error('[T05] /motion/upper_body_debug 不可用')
        return False
    req = SetBool.Request(); req.data = enable
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    resp = future.result()
    if resp:
        node.get_logger().info(
            f'[T05] upper_body_debug({enable}) => success={resp.success}  msg="{resp.message}"')
        return resp.success
    return False

def main():
    rclpy.init()
    node = Node('t05_upper_debug_py')

    # Step 1: 进入调试
    if not switch_debug(node, True):
        node.get_logger().warn('[T05] 进入上身调试失败（当前模式可能不支持），继续发布...')
    time.sleep(0.3)

    # Step 2: 10 Hz 发布上身关节指令，2 秒
    pub = node.create_publisher(UpperJointData, '/upper_body_debug/joint_cmd', 10)
    rate = node.create_rate(10)
    for i in range(20):
        if not rclpy.ok(): break
        msg = UpperJointData()
        msg.header.stamp    = node.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.time_ref        = 0.0
        msg.vel_scale       = 0.05  # 极低速度，安全测试
        msg.joint.name     = ['left_shoulder_pitch_joint', 'right_shoulder_pitch_joint']
        msg.joint.position = [0.05, 0.05]
        pub.publish(msg)
        if i % 10 == 0:
            node.get_logger().info(
                f'[T05] 发布 joint_cmd vel_scale={msg.vel_scale}'
                f'  pos={msg.joint.position}  frame#{i+1}')
        rclpy.spin_once(node, timeout_sec=0.05)
        rate.sleep()

    # Step 3: 退出调试
    switch_debug(node, False)
    node.get_logger().info('[T05] 完成')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
