#!/usr/bin/env python3
"""
Test Flow 2: 上肢调试完整序列
流程：
  STAND → WALK → (motion/upper_body_debug true) →
  发送姿态1(双肩前倾) → 等 2s → 发送姿态2(双臂外展) → 等 2s →
  发送姿态3(归零) → 等 2s → (motion/upper_body_debug false) → STAND
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode
from crb_ros_msg.msg import UpperJointData, JointStateData
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import time

# 手臂关节名称（与 /joint_states 中一致，不带 _joint 后缀）
ARM_JOINTS = [
    'left_shoulder_pitch',
    'left_shoulder_roll',
    'left_shoulder_yaw',
    'left_elbow_pitch',
    'left_wrist_yaw',
    'left_wrist_pitch',
    'left_wrist_roll',
    'right_shoulder_pitch',
    'right_shoulder_roll',
    'right_shoulder_yaw',
    'right_elbow_pitch',
    'right_wrist_yaw',
    'right_wrist_pitch',
    'right_wrist_roll',
    'waist_yaw',
    'head_yaw',
    'head_pitch',
]

# 姿态1：双肩前倾
POSE_SHOULDER_FWD = {
    'left_shoulder_pitch':  0.5,
    'right_shoulder_pitch': 0.5,
    'left_elbow_pitch':    -0.5,
    'right_elbow_pitch':   -0.5,
}

# 姿态2：双臂外展（恢复肩仰角，外展）
POSE_SPREAD_ARMS = {
    'left_shoulder_pitch':   0.1,
    'left_shoulder_roll':    0.4,
    'right_shoulder_pitch':  0.1,
    'right_shoulder_roll':  -0.4,
}

# 姿态3：全部归零
POSE_ZERO = {j: 0.0 for j in ARM_JOINTS}


class UpperDebugFlowTest(Node):
    def __init__(self):
        super().__init__('upper_debug_flow_test')
        self.latest_arm = None

        self.arm_sub = self.create_subscription(
            JointStateData, '/joint_states', self._arm_cb, 10)

        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_debug = self.create_client(SetBool, '/motion/upper_body_debug')
        self.cmd_pub = self.create_publisher(
            UpperJointData, '/upper_body_debug/joint_cmd', 10)

    def _arm_cb(self, msg):
        self.latest_arm = msg.joint

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

    def call_debug(self, enable: bool):
        if not self.cli_debug.wait_for_service(timeout_sec=5.0):
            return False, 'service not available'
        req = SetBool.Request()
        req.data = enable
        future = self.cli_debug.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.success, r.message
        return False, 'timeout'

    def get_arm_snapshot(self):
        """返回关键手臂关节当前实测位置（从 /joint_states）"""
        for _ in range(20):
            rclpy.spin_once(self, timeout_sec=0.05)
        if not self.latest_arm:
            return {}
        return {
            n: round(self.latest_arm.position[i], 4)
            for i, n in enumerate(self.latest_arm.name)
            if n in ('left_shoulder_pitch', 'right_shoulder_pitch',
                     'left_shoulder_roll', 'right_shoulder_roll',
                     'left_elbow_pitch', 'right_elbow_pitch')
        }

    def send_pose(self, pose_dict: dict, duration_s: float = 2.0, rate: int = 50,
                  kp=None, kd=None):
        """以 rate Hz 持续发送目标关节位置 duration_s 秒，可选附带 kp/kd"""
        end = time.time() + duration_s
        count = 0
        names = list(pose_dict.keys())
        while time.time() < end:
            msg = UpperJointData()
            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.time_ref = 0.1
            msg.vel_scale = 0.3
            js = JointState()
            js.name = names
            js.position = [float(pose_dict[n]) for n in names]
            js.velocity = [0.0] * len(names)
            js.effort = [0.0] * len(names)
            msg.joint = js
            if kp is not None:
                msg.kp = list(kp)
            if kd is not None:
                msg.kd = list(kd)
            self.cmd_pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=1.0 / rate)
            count += 1
        return count

    def run(self):
        results = []

        # ── 步骤 1: 确认 / 切换到 WALK 模式 ─────────────────────
        print('\n[步骤 1] 切换到 WALK 模式...')
        _, cur = self.get_mode()
        if cur != 'WALK':
            if cur != 'STAND':
                self.set_mode('ZERO')
                time.sleep(1.0)
                self.set_mode('STAND')
                time.sleep(1.0)
            ok1 = self.set_mode('WALK')
            time.sleep(0.5)
        else:
            ok1 = True
        _, cur = self.get_mode()
        print(f'  当前模式: {cur}')
        results.append(('切换到 WALK 模式', cur == 'WALK', f'当前={cur}'))

        # ── 步骤 2: 进入上肢调试模式 ─────────────────────────────
        print('\n[步骤 2] /motion/upper_body_debug → true (进入上肢调试)...')
        ok2, msg2 = self.call_debug(True)
        time.sleep(0.3)
        print(f'  结果: success={ok2}, message="{msg2}"')
        results.append(('进入上肢调试模式', ok2, f'success={ok2}, msg="{msg2}"'))

        # ── 步骤 3: 采集初始手臂位置 ─────────────────────────────
        init_snap = self.get_arm_snapshot()
        print(f'\n[步骤 3] 初始手臂关节: {init_snap}')
        results.append(('采集初始关节位置', bool(init_snap), str(init_snap)))

        # ── 步骤 4: 发送姿态1 —— 双肩前倾 + 肘关节弯曲 ──────────
        print('\n[步骤 4] 发送姿态1：双肩前倾 shoulder_pitch=0.4, elbow=-0.6, 持续 2s...')
        n4 = self.send_pose(POSE_SHOULDER_FWD, 2.0)
        snap4 = self.get_arm_snapshot()
        print(f'  执行后: {snap4}')
        lsp = snap4.get('left_shoulder_pitch', 0.0)
        rsp = snap4.get('right_shoulder_pitch', 0.0)
        p4_ok = abs(lsp - 0.5) < 0.2 or abs(rsp - 0.5) < 0.2
        results.append(('姿态1 双肩前倾', p4_ok,
                         f'发布{n4}帧, left_shoulder_pitch={lsp:.4f}(目标0.5), '
                         f'right={rsp:.4f}(目标0.5)'))

        # ── 步骤 5: 发送姿态2 —— 双臂外展 ───────────────────────
        print('\n[步骤 5] 发送姿态2：双臂外展 shoulder_roll=±0.3, 持续 2s...')
        n5 = self.send_pose(POSE_SPREAD_ARMS, 2.0)
        snap5 = self.get_arm_snapshot()
        print(f'  执行后: {snap5}')
        lsr = snap5.get('left_shoulder_roll', 0.0)
        rsr = snap5.get('right_shoulder_roll', 0.0)
        p5_ok = abs(lsr - 0.4) < 0.2 or abs(rsr + 0.4) < 0.2
        results.append(('姿态2 双臂外展', p5_ok,
                         f'发布{n5}帧, left_shoulder_roll={lsr:.4f}(目标0.4), '
                         f'right_shoulder_roll={rsr:.4f}(目标-0.4)'))

        # ── 步骤 6: 发送姿态3 —— 全部归零 ───────────────────────
        print('\n[步骤 6] 发送姿态3：全部归零, 持续 2s...')
        n6 = self.send_pose(POSE_ZERO, 2.0)
        snap6 = self.get_arm_snapshot()
        print(f'  执行后: {snap6}')
        max_dev = max((abs(v) for v in snap6.values()), default=0.0)
        p6_ok = max_dev < 0.25
        results.append(('姿态3 全部归零', p6_ok,
                         f'发布{n6}帧, 最大偏差={max_dev:.4f}rad (阈值0.25)'))

        # ── 步骤 7: 退出上肢调试模式 ─────────────────────────────
        print('\n[步骤 7] /motion/upper_body_debug → false (退出调试)...')
        ok7, msg7 = self.call_debug(False)
        print(f'  结果: success={ok7}, message="{msg7}"')
        results.append(('退出上肢调试模式', ok7, f'success={ok7}, msg="{msg7}"'))

        # ── 步骤 8: 切回 STAND 模式 ──────────────────────────────
        print('\n[步骤 8] set_robot_mode → STAND...')
        ok8 = self.set_mode('STAND')
        time.sleep(0.5)
        _, cur8 = self.get_mode()
        print(f'  当前模式: {cur8}')
        results.append(('退出切回 STAND', ok8, f'当前模式={cur8}'))

        return results


def main():
    rclpy.init()
    node = UpperDebugFlowTest()
    print('=' * 60)
    print('  Test Flow 2: 上肢调试完整序列')
    print('  WALK → upper_body_debug → 3组姿态 → 退出 → STAND')
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
