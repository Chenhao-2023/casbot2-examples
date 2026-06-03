#!/usr/bin/env python3
"""T01: 查询机器人运控状态 — 对应接口文档 5.3"""
import rclpy
from rclpy.node import Node
from crb_ros_msg.srv import GetRobotState
from std_msgs.msg import String

STATE_MAP = {
    0: 'UNDEFINED', 1: 'DAMPING', 2: 'READY',
    3: 'STAND',     4: 'WALKING', 5: 'RUNNING',
    255: 'EMERGENCY_STOP',
}

def main():
    rclpy.init()
    node = Node('t01_get_state_py')

    # --- 1. Service 查询状态 ---
    cli = node.create_client(GetRobotState, 'get_robot_state_srv_hl')
    node.get_logger().info('[T01] 等待 /get_robot_state 服务...')
    if not cli.wait_for_service(timeout_sec=5.0):
        node.get_logger().error('[T01] 服务不可用，超时退出')
        rclpy.shutdown(); return

    req = GetRobotState.Request()
    req.start = True
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    resp = future.result()
    if resp:
        state = resp.state
        name = STATE_MAP.get(state, 'UNKNOWN')
        node.get_logger().info(f'[T01] GetRobotState => state={state} ({name})')
    else:
        node.get_logger().error('[T01] Service 调用失败')

    # --- 2. Topic 订阅状态字符串 ---
    node.get_logger().info('[T01] 订阅 /motion/status (3 秒)...')
    last = ['']
    def status_cb(msg: String):
        if msg.data != last[0]:
            last[0] = msg.data
            node.get_logger().info(f'[T01] /motion/status: {msg.data}')
    node.create_subscription(String, '/motion/status', status_cb, 10)

    import time; deadline = time.time() + 3.0
    while time.time() < deadline and rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)

    node.get_logger().info('[T01] 完成')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
