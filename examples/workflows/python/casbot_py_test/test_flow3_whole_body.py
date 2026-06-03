#!/usr/bin/env python3
"""
Test Flow 3: 全身调试模式 — 腰部旋转 + 头部运动序列
接口说明：
  WHOLE_BODY_DEBUG 模式通过 /motion/joint_cmd (crb_ros_msg/WholeBodyJointData) 接收命令
  关节名使用 _joint 后缀（与 joint_info.cpp 中 gJointNameToId 一致）
  name / position / velocity / effort 数组大小必须相同

流程：
  STAND → WALK → (whole_body_debug true) →
  腰部左转 (waist_yaw_joint=0.3) → 2s → 头部低头 (head_pitch_joint=0.2) → 2s →
  全部归零 → 2s → (whole_body_debug false) → STAND
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode
from crb_ros_msg.msg import WholeBodyJointData, JointStateData
from sensor_msgs.msg import JointState
import time


def make_joint_cmd(names, positions, node=None, kp=None, kd=None):
    """/motion/joint_cmd 要求 WholeBodyJointData，joint 内 name/position/velocity/effort 等长"""
    msg = WholeBodyJointData()
    if node:
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


class WholeBodyDebugTest(Node):
    def __init__(self):
        super().__init__('whole_body_debug_test')
        self.latest_joint = None

        self.joint_sub = self.create_subscription(
            JointStateData, '/joint_states', self._joint_cb, 10)

        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_wb = self.create_client(SetBool, '/motion/whole_body_debug')

        # WHOLE_BODY_DEBUG 使用 /motion/joint_cmd，类型 crb_ros_msg/WholeBodyJointData
        self.cmd_pub = self.create_publisher(WholeBodyJointData, '/motion/joint_cmd', 10)

    def _joint_cb(self, msg):
        self.latest_joint = msg.joint

    def set_mode(self, mode_name: str):
        if not self.cli_set_mode.wait_for_service(timeout_sec=5.0):
            return False
        req = SetRobotMode.Request()
        req.mode_name = mode_name
        future = self.cli_set_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        return future.done() and future.result().success

    def get_mode(self):
        if not self.cli_get_mode.wait_for_service(timeout_sec=5.0):
            return -1, '?'
        req = GetRobotMode.Request()
        future = self.cli_get_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.mode, r.mode_name
        return -1, '?'

    def call_wb(self, enable: bool):
        if not self.cli_wb.wait_for_service(timeout_sec=5.0):
            return False, 'service not available'
        req = SetBool.Request()
        req.data = enable
        future = self.cli_wb.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.success, r.message
        return False, 'timeout'

    def get_joint(self, short_name: str):
        """从 /joint_states 读取关节实测值（short_name 不含 _joint）"""
        deadline = time.time() + 3.0
        while time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.latest_joint:
                break
        if not self.latest_joint:
            return None
        for i, n in enumerate(self.latest_joint.name):
            if n == short_name:
                return round(self.latest_joint.position[i], 4)
        return None

    def send_pose(self, joint_dict: dict, duration_s: float = 2.0, rate: int = 50):
        """
        joint_dict: {joint_name_with_joint_suffix: position}
        持续发送 duration_s 秒
        """
        end = time.time() + duration_s
        count = 0
        names = list(joint_dict.keys())
        positions = list(joint_dict.values())
        while time.time() < end:
            msg = make_joint_cmd(names, positions, self)
            self.cmd_pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=1.0 / rate)
            count += 1
        return count

    def run(self):
        results = []

        # ── 步骤 1: 切换到 WALK 模式 ─────────────────────────────
        print('\n[步骤 1] 切换到 WALK 模式...')
        _, cur = self.get_mode()
        if cur != 'WALK':
            if cur not in ('STAND', 'ZERO'):
                self.set_mode('ZERO')
                time.sleep(1.0)
                self.set_mode('STAND')
                time.sleep(1.0)
            elif cur == 'ZERO':
                self.set_mode('STAND')
                time.sleep(1.0)
            self.set_mode('WALK')
            time.sleep(0.5)
        _, cur = self.get_mode()
        print(f'  当前模式: {cur}')
        results.append(('切换到 WALK 模式', cur == 'WALK', f'当前={cur}'))

        # ── 步骤 2: 进入全身调试模式 ─────────────────────────────
        print('\n[步骤 2] /motion/whole_body_debug → true ...')
        ok2, msg2 = self.call_wb(True)
        time.sleep(0.5)
        print(f'  结果: success={ok2}, message="{msg2}"')
        results.append(('进入全身调试模式', ok2, f'success={ok2}, msg="{msg2}"'))

        # ── 步骤 3: 采集初始腰/头位置 ───────────────────────────
        waist_init = self.get_joint('waist_yaw')
        head_init  = self.get_joint('head_pitch')
        print(f'\n[步骤 3] 初始: waist_yaw={waist_init}, head_pitch={head_init}')
        results.append(('采集初始关节位置', waist_init is not None,
                         f'waist_yaw={waist_init}, head_pitch={head_init}'))

        # ── 步骤 4: 腰部左转 0.3 rad ─────────────────────────────
        print('\n[步骤 4] 发送腰部左转 waist_yaw_joint=0.3 rad，持续 2s...')
        n4 = self.send_pose({'waist_yaw_joint': 0.3}, 2.0)
        waist4 = self.get_joint('waist_yaw')
        print(f'  执行后 waist_yaw={waist4} (目标=0.3, 发布{n4}帧)')
        w4_ok = waist4 is not None and abs(waist4 - 0.3) < 0.2
        results.append(('腰部左转 (waist_yaw=0.3)', w4_ok,
                         f'实测={waist4}, 目标=0.3, '
                         f'偏差={abs((waist4 or 0) - 0.3):.4f}'))

        # ── 步骤 5: 头部低头 0.2 rad + 保持腰部 ─────────────────
        print('\n[步骤 5] 发送头部低头 head_pitch_joint=0.2 rad + 腰部保持 0.3，持续 2s...')
        n5 = self.send_pose({'waist_yaw_joint': 0.3, 'head_pitch_joint': 0.2}, 2.0)
        head5   = self.get_joint('head_pitch')
        waist5  = self.get_joint('waist_yaw')
        print(f'  执行后 head_pitch={head5} (目标=0.2), waist_yaw={waist5} (发布{n5}帧)')
        h5_ok = head5 is not None and abs(head5 - 0.2) < 0.2
        results.append(('头部低头 (head_pitch=0.2)', h5_ok,
                         f'实测={head5}, 目标=0.2, '
                         f'偏差={abs((head5 or 0) - 0.2):.4f}'))

        # ── 步骤 6: 全部归零 ─────────────────────────────────────
        print('\n[步骤 6] 全部归零，持续 2s...')
        n6 = self.send_pose({
            'waist_yaw_joint': 0.0, 'head_pitch_joint': 0.0, 'head_yaw_joint': 0.0,
            'left_shoulder_pitch_joint': 0.0,  'right_shoulder_pitch_joint': 0.0,
            'left_shoulder_roll_joint': 0.0,   'right_shoulder_roll_joint': 0.0,
            'left_elbow_pitch_joint': 0.0,     'right_elbow_pitch_joint': 0.0,
        }, 2.0)
        waist_z = self.get_joint('waist_yaw')
        head_z  = self.get_joint('head_pitch')
        print(f'  归零后: waist_yaw={waist_z}, head_pitch={head_z} (发布{n6}帧)')
        zero_ok = (waist_z is not None and abs(waist_z) < 0.15 and
                   head_z is not None and abs(head_z) < 0.15)
        results.append(('全部归零', zero_ok,
                         f'waist_yaw={waist_z}(±0.15), head_pitch={head_z}(±0.15)'))

        # ── 步骤 7: 退出全身调试模式 ─────────────────────────────
        print('\n[步骤 7] /motion/whole_body_debug → false ...')
        ok7, msg7 = self.call_wb(False)
        print(f'  结果: success={ok7}, message="{msg7}"')
        results.append(('退出全身调试模式', ok7, f'success={ok7}, msg="{msg7}"'))

        # ── 步骤 8: 切回 STAND ────────────────────────────────────
        print('\n[步骤 8] ZERO → STAND...')
        self.set_mode('ZERO')
        time.sleep(1.5)
        ok8 = self.set_mode('STAND')
        time.sleep(1.0)
        _, cur8 = self.get_mode()
        print(f'  当前模式: {cur8}')
        results.append(('退出切回 STAND', ok8, f'当前模式={cur8}'))

        return results


def main():
    rclpy.init()
    node = WholeBodyDebugTest()
    print('=' * 60)
    print('  Test Flow 3: 全身调试腰部/头部运动序列')
    print('  WALK → whole_body_debug → 腰转+低头+归零 → STAND')
    print('  命令话题: /motion/joint_cmd (crb_ros_msg/WholeBodyJointData)')
    print('=' * 60)

    try:
        results = node.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        results = [('异常', False, str(e))]
    finally:
        node.destroy_node()
        rclpy.shutdown()

    print('\n' + '=' * 60)
    print('  测试结果汇总')
    print('=' * 60)
    all_ok = True
    for step, ok, detail in results:
        status = '✓ PASS' if ok else '✗ FAIL'
        all_ok = all_ok and ok
        print(f'  [{status}] {step}')
        print(f'          {detail}')
    print('-' * 60)
    print(f'  总体结果: {"✓ 全部通过" if all_ok else "✗ 存在失败项"}')
    print('=' * 60)


if __name__ == '__main__':
    main()
