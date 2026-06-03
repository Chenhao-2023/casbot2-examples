#!/usr/bin/env python3
"""T02: 切换遥操作 / 自主模式 — 对应接口文档 switch_teleoperation / switch_autonomous"""
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
import time

def call_set_bool(node: Node, srv_name: str, data: bool, label: str) -> bool:
    cli = node.create_client(SetBool, srv_name)
    node.get_logger().info(f'[T02] 等待 {srv_name} ...')
    if not cli.wait_for_service(timeout_sec=5.0):
        node.get_logger().error(f'[T02] {srv_name} 不可用')
        return False
    req = SetBool.Request(); req.data = data
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    resp = future.result()
    if resp:
        node.get_logger().info(
            f'[T02] {label}({data}) => success={resp.success}  msg="{resp.message}"')
        return resp.success
    node.get_logger().error(f'[T02] {label} 调用无响应')
    return False

def main():
    rclpy.init()
    node = Node('t02_switch_mode_py')

    node.get_logger().info('[T02] === 切换遥操作模式 ===')
    call_set_bool(node, '/switch_teleoperation', True,  'switch_teleoperation')
    time.sleep(2.0)
    call_set_bool(node, '/switch_teleoperation', False, 'switch_teleoperation')
    time.sleep(1.0)

    node.get_logger().info('[T02] === 切换自主（动作播放）模式 ===')
    call_set_bool(node, '/switch_autonomous', True,  'switch_autonomous')
    time.sleep(2.0)
    call_set_bool(node, '/switch_autonomous', False, 'switch_autonomous')

    node.get_logger().info('[T02] 完成')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
