#!/usr/bin/env python3
"""T03: 订阅关节状态与 IMU — 对应接口文档 5.8 传感器数据订阅"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu
import time

class SensorMonitor(Node):
    def __init__(self):
        super().__init__('t03_joint_states_py')
        self._joint_cnt = 0
        self._imu_cnt   = 0
        self.create_subscription(JointState, '/joint_states', self._joint_cb, 10)
        self.create_subscription(Imu,        '/imu',          self._imu_cb,   10)

    def _joint_cb(self, msg: JointState):
        self._joint_cnt += 1
        if self._joint_cnt % 100 == 1:
            self.get_logger().info(
                f'[T03] /joint_states  joints={len(msg.name)}  frame#{self._joint_cnt}')
            for i, name in enumerate(msg.name[:3]):
                pos = msg.position[i] if len(msg.position) > i else 0.0
                vel = msg.velocity[i] if len(msg.velocity) > i else 0.0
                self.get_logger().info(
                    f'[T03]   {name:<35s} pos={pos:7.4f} rad  vel={vel:7.4f} rad/s')

    def _imu_cb(self, msg: Imu):
        self._imu_cnt += 1
        if self._imu_cnt % 200 == 1:
            o = msg.orientation
            self.get_logger().info(
                f'[T03] /imu  orient w={o.w:.3f} x={o.x:.3f} y={o.y:.3f} z={o.z:.3f}'
                f'  frame#{self._imu_cnt}')

def main():
    rclpy.init()
    node = SensorMonitor()
    node.get_logger().info('[T03] 订阅 /joint_states 和 /imu，持续 5 秒...')
    deadline = time.time() + 5.0
    while time.time() < deadline and rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)
    node.get_logger().info(
        f'[T03] 完成：joint_states {node._joint_cnt} 帧，imu {node._imu_cnt} 帧')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
