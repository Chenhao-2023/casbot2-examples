#!/usr/bin/env python3
"""验证 /joint_states 与 /joint_control 是否携带当前 kp/kd。"""

import sys
import time

import rclpy
from rclpy.node import Node
from crb_ros_msg.msg import JointStateData


class JointStatePdTest(Node):
    def __init__(self):
        super().__init__('joint_state_pd_test')
        self.states_msg = None
        self.control_msg = None
        self.create_subscription(JointStateData, '/joint_states', self._states_cb, 10)
        self.create_subscription(JointStateData, '/joint_control', self._control_cb, 10)

    def _states_cb(self, msg):
        self.states_msg = msg

    def _control_cb(self, msg):
        self.control_msg = msg

    def wait_msgs(self, timeout=10.0):
        end = time.time() + timeout
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.states_msg and self.control_msg:
                return True
        return False

    def check_msg(self, msg):
        n = len(msg.joint.name)
        ok_len = (len(msg.kp) == n and len(msg.kd) == n and len(msg.joint.position) == n)
        has_nonzero = any(abs(k) > 1e-6 for k in msg.kp) and any(abs(k) > 1e-6 for k in msg.kd)
        return ok_len and has_nonzero


def main():
    rclpy.init()
    node = JointStatePdTest()
    print('等待 /joint_states 与 /joint_control (JointStateData)...')
    if not node.wait_msgs():
        print('FAIL: 超时未收到消息，请先启动 hlorin')
        node.destroy_node(); rclpy.shutdown(); sys.exit(1)

    ok_states = node.check_msg(node.states_msg)
    ok_control = node.check_msg(node.control_msg)
    print(f'[joint_states] {"PASS" if ok_states else "FAIL"}')
    print(f'[joint_control] {"PASS" if ok_control else "FAIL"}')

    node.destroy_node()
    rclpy.shutdown()
    all_ok = ok_states and ok_control
    print('总体:', 'PASS' if all_ok else 'FAIL')
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
