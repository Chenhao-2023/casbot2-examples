#!/usr/bin/env python3
"""
Test Flow: Debug 模式 kp/kd 开关验证 (TC1-TC5)
"""

import argparse
import subprocess
import sys
import time

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode
from crb_ros_msg.msg import WholeBodyJointData, UpperJointData, JointStateData
from sensor_msgs.msg import JointState


def make_wb_cmd(node, names, positions, kp=None, kd=None):
    msg = WholeBodyJointData()
    msg.header.stamp = node.get_clock().now().to_msg()
    js = JointState()
    js.name = list(names)
    js.position = list(positions)
    js.velocity = [0.0] * len(names)
    js.effort = [0.0] * len(names)
    msg.joint = js
    if kp is not None:
        msg.kp = list(kp)
    if kd is not None:
        msg.kd = list(kd)
    return msg


def make_upper_cmd(node, names, positions, kp=None, kd=None):
    msg = UpperJointData()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.time_ref = 0.1
    msg.vel_scale = 0.3
    js = JointState()
    js.name = list(names)
    js.position = list(positions)
    js.velocity = [0.0] * len(names)
    js.effort = [0.0] * len(names)
    msg.joint = js
    if kp is not None:
        msg.kp = list(kp)
    if kd is not None:
        msg.kd = list(kd)
    return msg


class DebugKpKdTest(Node):
    def __init__(self):
        super().__init__('debug_kp_kd_test')
        self.latest_joint = None
        self.create_subscription(JointStateData, '/joint_states', self._joint_cb, 10)

        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_wb = self.create_client(SetBool, '/motion/whole_body_debug')
        self.cli_ub = self.create_client(SetBool, '/motion/upper_body_debug')

        self.wb_pub = self.create_publisher(WholeBodyJointData, '/motion/joint_cmd', 10)
        self.ub_pub = self.create_publisher(UpperJointData, '/upper_body_debug/joint_cmd', 10)

    def _joint_cb(self, msg):
        self.latest_joint = msg.joint

    def wait_services(self, timeout=10.0):
        deadline = time.time() + timeout
        for cli in (self.cli_set_mode, self.cli_get_mode, self.cli_wb, self.cli_ub):
            while not cli.wait_for_service(timeout_sec=0.5):
                if time.time() > deadline:
                    return False
        return True

    def set_mode(self, mode_name: str):
        req = SetRobotMode.Request()
        req.mode_name = mode_name
        future = self.cli_set_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        return future.done() and future.result().success

    def get_mode(self):
        req = GetRobotMode.Request()
        future = self.cli_get_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.mode, r.mode_name
        return -1, '?'

    def call_srv(self, cli, enable: bool):
        req = SetBool.Request()
        req.data = enable
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.success, r.message
        return False, 'timeout'

    def get_joint(self, short_name: str, wait_s=2.0):
        deadline = time.time() + wait_s
        while time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.latest_joint:
                break
        if not self.latest_joint:
            return None
        for i, n in enumerate(self.latest_joint.name):
            if n == short_name:
                return self.latest_joint.position[i]
        return None

    def publish_wb(self, names, positions, duration_s=1.5, kp=None, kd=None):
        end = time.time() + duration_s
        while time.time() < end:
            self.wb_pub.publish(make_wb_cmd(self, names, positions, kp, kd))
            rclpy.spin_once(self, timeout_sec=0.02)

    def publish_ub(self, names, positions, duration_s=1.5, kp=None, kd=None):
        end = time.time() + duration_s
        while time.time() < end:
            self.ub_pub.publish(make_upper_cmd(self, names, positions, kp, kd))
            rclpy.spin_once(self, timeout_sec=0.02)

    def run_tc1(self):
        self.set_mode('WALK')
        ok, msg = self.call_srv(self.cli_wb, True)
        if not ok:
            return False, f'进入全身调试失败: {msg}'
        init = self.get_joint('waist_yaw')
        self.publish_wb(['waist_yaw_joint'], [0.3], 2.0)
        final = self.get_joint('waist_yaw')
        self.call_srv(self.cli_wb, False)
        moved = (init is not None and final is not None and abs(final - 0.3) < 0.25)
        return moved, f'waist_yaw: {init} -> {final}'

    def run_tc2(self):
        self.set_mode('WALK')
        ok, msg = self.call_srv(self.cli_ub, True)
        if not ok:
            return False, f'进入上身调试失败: {msg}'
        init = self.get_joint('left_shoulder_pitch')
        self.publish_ub(['left_shoulder_pitch'], [0.4], 2.0)
        final = self.get_joint('left_shoulder_pitch')
        self.call_srv(self.cli_ub, False)
        moved = (init is not None and final is not None and abs(final - 0.4) < 0.25)
        return moved, f'left_shoulder_pitch: {init} -> {final}'

    def run_tc3(self):
        self.set_mode('WALK')
        ok, msg = self.call_srv(self.cli_wb, True)
        if not ok:
            return False, f'进入全身调试失败: {msg}'
        init = self.get_joint('head_pitch')
        self.publish_wb(['head_pitch_joint'], [0.25], duration_s=2.0, kp=[50.0], kd=[5.0])
        final = self.get_joint('head_pitch')
        self.call_srv(self.cli_wb, False)
        moved = (init is not None and final is not None and abs(final - 0.25) < 0.25)
        return moved, f'head_pitch: {init} -> {final}'

    def run_tc4(self):
        self.set_mode('WALK')
        ok, msg = self.call_srv(self.cli_wb, True)
        if not ok:
            return False, f'进入全身调试失败: {msg}'
        init = self.get_joint('waist_yaw')
        self.publish_wb(['waist_yaw_joint'], [0.35], 2.0)
        final = self.get_joint('waist_yaw')
        self.call_srv(self.cli_wb, False)
        rejected = abs((final or 0) - 0.35) > 0.15 if final is not None else True
        return rejected, f'waist_yaw: {init} -> {final}'

    def run_tc5(self):
        try:
            out = subprocess.run(
                ['ros2', 'topic', 'info', '/motion/joint_cmd'],
                capture_output=True, text=True, timeout=10.0,
            )
            text = out.stdout + out.stderr
            ok = 'WholeBodyJointData' in text or 'whole_body_joint_data' in text.lower()
            return ok, text.strip()
        except Exception as e:
            return False, str(e)


TC_RUNNERS = {1: 'run_tc1', 2: 'run_tc2', 3: 'run_tc3', 4: 'run_tc4', 5: 'run_tc5'}


def main():
    parser = argparse.ArgumentParser(description='Debug kp/kd 开关测试 TC1-TC5')
    parser.add_argument('--tc', type=int, nargs='+', default=[1, 2, 3, 4, 5])
    args = parser.parse_args()

    rclpy.init()
    node = DebugKpKdTest()
    if not node.wait_services():
        print('ERROR: ROS 服务不可用，请先启动 hlorin MuJoCo 仿真')
        node.destroy_node(); rclpy.shutdown(); sys.exit(1)

    results = []
    try:
        for tc in args.tc:
            runner = getattr(node, TC_RUNNERS.get(tc, ''), None)
            if runner is None:
                results.append((f'TC{tc}', False, '未知用例'))
                continue
            ok, detail = runner()
            results.append((f'TC{tc}', ok, detail))
    finally:
        node.destroy_node()
        rclpy.shutdown()

    all_ok = True
    for name, ok, detail in results:
        print(f'[{ "PASS" if ok else "FAIL"}] {name}: {detail}')
        all_ok = all_ok and ok
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
