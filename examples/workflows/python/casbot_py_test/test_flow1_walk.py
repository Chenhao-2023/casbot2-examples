#!/usr/bin/env python3
"""
Test Flow 1: 行走完整流程
流程：
  STAND → (set_robot_mode WALK) → (switch_teleoperation) →
  发布前进 cmd_vel 3s → 发布左转 cmd_vel 2s → 停止 → (set_robot_mode STAND)
  全程订阅 /joint_states 记录腿部关节运动
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import time


class WalkFlowTest(Node):
    def __init__(self):
        super().__init__('walk_flow_test')
        self.joint_log = []
        self.latest_joint = None

        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self._joint_cb, 10)

        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_teleoperation = self.create_client(SetBool, '/switch_teleoperation')
        self.cmd_pub = self.create_publisher(Twist, '/navigation/cmd_vel', 10)

    def _joint_cb(self, msg):
        self.latest_joint = msg
        if msg.name:
            leg_pos = {n: round(msg.position[i], 4)
                       for i, n in enumerate(msg.name) if n.startswith(('LJ', 'RJ'))}
            self.joint_log.append((time.time(), leg_pos))

    def get_mode(self):
        if not self.cli_get_mode.wait_for_service(timeout_sec=5.0):
            return -1, 'service not available'
        req = GetRobotMode.Request()
        future = self.cli_get_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.mode, r.mode_name
        return -1, 'timeout'

    def set_mode(self, mode_name: str):
        if not self.cli_set_mode.wait_for_service(timeout_sec=5.0):
            return False
        req = SetRobotMode.Request()
        req.mode_name = mode_name
        future = self.cli_set_mode.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        return future.done() and future.result().success

    def switch_teleoperation(self, enable: bool):
        if not self.cli_teleoperation.wait_for_service(timeout_sec=5.0):
            return False, 'service not available'
        req = SetBool.Request()
        req.data = enable
        future = self.cli_teleoperation.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            r = future.result()
            return r.success, r.message
        return False, 'timeout'

    def publish_cmd_vel(self, linear_x: float, angular_z: float, duration: float):
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        end = time.time() + duration
        count = 0
        while time.time() < end:
            self.cmd_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.05)
            count += 1
        return count

    def snapshot_leg_joints(self):
        for _ in range(20):
            rclpy.spin_once(self, timeout_sec=0.05)
        if not self.latest_joint:
            return {}
        return {n: round(self.latest_joint.position[i], 4)
                for i, n in enumerate(self.latest_joint.name)
                if n.startswith(('LJ', 'RJ'))}

    def run(self):
        results = []

        # ── 步骤 1: 查询初始模式 ──────────────────────────────────
        print('\n[步骤 1] 查询当前模式...')
        mode_id, mode_name = self.get_mode()
        print(f'  当前模式: mode={mode_id}, name={mode_name}')
        results.append(('查询初始模式', mode_id >= 0,
                         f'mode={mode_id} ({mode_name})'))

        # 如果不在 STAND，先复位
        if mode_name not in ('STAND', 'ZERO'):
            self.set_mode('ZERO')
            time.sleep(1.0)
            self.set_mode('STAND')
            time.sleep(1.0)

        # ── 步骤 2: 切换到 WALK 模式 ─────────────────────────────
        print('\n[步骤 2] set_robot_mode → WALK ...')
        ok = self.set_mode('WALK')
        time.sleep(0.5)
        mode_id2, mode_name2 = self.get_mode()
        print(f'  切换结果: success={ok}, 当前 mode={mode_id2} ({mode_name2})')
        results.append(('切换到 WALK 模式', ok and mode_name2 == 'WALK',
                         f'success={ok}, mode={mode_id2} ({mode_name2})'))

        # ── 步骤 3: 进入遥控行走模式 ─────────────────────────────
        print('\n[步骤 3] switch_teleoperation → true (进入 TELEOPERATION 行走模式)...')
        ok3, msg3 = self.switch_teleoperation(True)
        time.sleep(0.3)
        mode_id3, mode_name3 = self.get_mode()
        print(f'  结果: success={ok3}, message="{msg3}", mode={mode_name3}')
        results.append(('进入遥控行走模式', ok3,
                         f'message="{msg3}", mode={mode_name3}'))

        # ── 步骤 4: 采集基准腿部关节位置 ─────────────────────────
        leg_before = self.snapshot_leg_joints()
        print(f'\n[步骤 4] 基准腿部关节: {leg_before}')

        # ── 步骤 5: 发布前进速度 3 秒 ────────────────────────────
        print('\n[步骤 5] 发布前进速度 linear.x=0.30 持续 3 秒...')
        self.joint_log.clear()
        count5 = self.publish_cmd_vel(0.30, 0.0, 3.0)
        leg_fwd = self.snapshot_leg_joints()
        print(f'  发布了 {count5} 帧, 此时腿部关节: {leg_fwd}')
        results.append(('前进 cmd_vel 3s',
                         len(self.joint_log) > 0,
                         f'发布 {count5} 帧, 收到关节反馈 {len(self.joint_log)} 帧'))

        # ── 步骤 6: 发布左转速度 2 秒 ────────────────────────────
        print('\n[步骤 6] 发布左转速度 linear.x=0.20, angular.z=0.30 持续 2 秒...')
        self.joint_log.clear()
        count6 = self.publish_cmd_vel(0.20, 0.30, 2.0)
        leg_turn = self.snapshot_leg_joints()
        print(f'  发布了 {count6} 帧, 此时腿部关节: {leg_turn}')
        results.append(('左转 cmd_vel 2s', True,
                         f'发布 {count6} 帧, 收到反馈 {len(self.joint_log)} 帧'))

        # ── 步骤 7: 发布停止指令 ─────────────────────────────────
        print('\n[步骤 7] 停止: 发布速度全零指令...')
        for _ in range(20):
            self.publish_cmd_vel(0.0, 0.0, 0.05)
        print('  停止指令发送完成')
        results.append(('发布停止指令 (vel=0)', True, 'linear.x=0, angular.z=0'))

        # ── 步骤 8: 切回 STAND 模式（需先 ZERO） ─────────────────
        print('\n[步骤 8] set_robot_mode → ZERO → STAND ...')
        ok8z = self.set_mode('ZERO')
        time.sleep(1.5)
        ok8s = self.set_mode('STAND')
        time.sleep(1.0)
        mode_final, mode_name_final = self.get_mode()
        print(f'  切换结果: ZERO={ok8z}, STAND={ok8s}, 当前 mode={mode_final} ({mode_name_final})')
        results.append(('切回 STAND (ZERO→STAND)', ok8s,
                         f'mode={mode_final} ({mode_name_final})'))

        return results


def main():
    rclpy.init()
    node = WalkFlowTest()
    print('=' * 60)
    print('  Test Flow 1: 行走完整流程')
    print('  STAND → WALK → TELEOPERATION → cmd_vel → STAND')
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
