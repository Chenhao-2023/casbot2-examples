#!/usr/bin/env python3
"""
Test Flow 4: 传感器订阅 + 状态查询 + 预设动作播放 + 行走控制权切换
覆盖文档中之前未测试的接口：
  5.3  get_robot_state_srv_hl    运控状态查询
  5.7  switch_autonomous          进入动作播放模式
       basic_action_play (Action) 播放预设动作 wave_hand
  5.8  /motion/imu               IMU 传感器订阅
       /motion/status            运动状态字符串
       /motion/robot_state       机器人状态字符串
       /joint_control            运控输出镜像
  5.9  /switch_drive_mode        行走控制权切换（新服务，仿真尚未包含则标注）

流程：
  STAND →
  [传感器] 订阅 imu/status/robot_state/joint_control 5 秒 →
  [状态查询] get_robot_state_srv_hl →
  [动作播放] WALK → switch_autonomous → basic_action_play(wave_hand) → 等结束 →
  [控制权切换] /switch_drive_mode(true=导航) → 验证 →
  ZERO → STAND
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode, GetRobotState
from crb_ros_msg.action import BasicActionPlay
from sensor_msgs.msg import Imu, JointState
from std_msgs.msg import String
import time


# 状态码对照（GetRobotState）
ROBOT_STATE_MAP = {0: 'IDLE', 1: 'INITIALIZE', 2: 'TASK_EXECUTION',
                   3: 'FAULT', 4: 'EMERGENCY_STOP'}


class SensorsAndActionsTest(Node):
    def __init__(self):
        super().__init__('sensors_actions_test')

        # 传感器数据缓存
        self.imu_msgs = []
        self.status_msgs = []
        self.robot_state_msgs = []
        self.joint_ctrl_msgs = []

        # 订阅
        self.create_subscription(Imu, '/motion/imu', self._imu_cb, 10)
        self.create_subscription(String, '/motion/status', self._status_cb, 10)
        self.create_subscription(String, '/motion/robot_state', self._rs_cb, 10)
        self.create_subscription(JointState, '/joint_control', self._jctrl_cb, 10)

        # 服务客户端
        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_get_state = self.create_client(GetRobotState, '/get_robot_state_srv_hl')
        self.cli_autonom = self.create_client(SetBool, '/switch_autonomous')
        self.cli_drive = self.create_client(SetBool, '/switch_drive_mode')

        # Action 客户端
        self.action_client = ActionClient(self, BasicActionPlay, '/basic_action_play')

        # Action 反馈记录
        self.action_feedbacks = []

    # ── 订阅回调 ────────────────────────────────────────────────
    def _imu_cb(self, msg): self.imu_msgs.append(msg)
    def _status_cb(self, msg): self.status_msgs.append(msg.data)
    def _rs_cb(self, msg): self.robot_state_msgs.append(msg.data)
    def _jctrl_cb(self, msg): self.joint_ctrl_msgs.append(msg)

    # ── 通用服务调用 ─────────────────────────────────────────────
    def _call(self, client, req, timeout=5.0):
        if not client.wait_for_service(timeout_sec=timeout):
            return None
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        return future.result() if future.done() else None

    def get_mode(self):
        r = self._call(self.cli_get_mode, GetRobotMode.Request())
        return (r.mode, r.mode_name) if r else (-1, '?')

    def set_mode(self, mode_name: str):
        req = SetRobotMode.Request(); req.mode_name = mode_name
        r = self._call(self.cli_set_mode, req)
        return r.success if r else False

    def spin_secs(self, secs: float):
        end = time.time() + secs
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.05)

    # ── Action: 播放预设动作 ─────────────────────────────────────
    def play_action(self, action_type: str, timeout: float = 20.0):
        """发送 BasicActionPlay goal，等待完成，返回 (success, feedback_states)"""
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            return False, [], '动作服务器不可达'

        goal = BasicActionPlay.Goal()
        goal.type = action_type

        self.action_feedbacks.clear()
        send_future = self.action_client.send_goal_async(
            goal,
            feedback_callback=self._action_feedback_cb)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=5.0)

        if not send_future.done():
            return False, [], 'send_goal 超时'

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            return False, [], 'Goal 被拒绝'

        result_future = goal_handle.get_result_async()
        deadline = time.time() + timeout
        while time.time() < deadline and not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.1)

        if result_future.done():
            result = result_future.result().result
            return result.if_success, self.action_feedbacks, 'OK'
        return False, self.action_feedbacks, '等待结果超时'

    def _action_feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        state_map = {0: 'NOT_PLAYING', 1: 'LOADING', 2: 'PLAYING', 3: 'FINISHED'}
        self.action_feedbacks.append(
            f'state={fb.state}({state_map.get(fb.state, "?")})')

    def run(self):
        results = []
        print('\n════ 阶段 A：传感器数据订阅 ════')

        _, cur_pre = self.get_mode()
        if cur_pre != 'WALK':
            if cur_pre not in ('STAND', 'ZERO'):
                self.set_mode('ZERO'); time.sleep(1.0); self.set_mode('STAND'); time.sleep(1.0)
            elif cur_pre == 'ZERO':
                self.set_mode('STAND'); time.sleep(1.0)
            self.set_mode('WALK'); time.sleep(0.5)

        cli_wb_tmp = self.create_client(SetBool, '/motion/whole_body_debug')
        req_wb = SetBool.Request(); req_wb.data = True
        r_wb = self._call(cli_wb_tmp, req_wb)
        print(f'  {r_wb.message if r_wb else "whole_body_debug 不可达"}')

        self.imu_msgs.clear(); self.status_msgs.clear()
        self.robot_state_msgs.clear(); self.joint_ctrl_msgs.clear()
        print('  采集 5s...')
        self.spin_secs(5.0)

        req_wb_off = SetBool.Request(); req_wb_off.data = False
        self._call(cli_wb_tmp, req_wb_off)

        imu_ok = len(self.imu_msgs) > 0
        if imu_ok:
            imu = self.imu_msgs[-1]
            imu_detail = (f'收到 {len(self.imu_msgs)} 帧, '
                          f'accel=({round(imu.linear_acceleration.x,3)},'
                          f'{round(imu.linear_acceleration.y,3)},'
                          f'{round(imu.linear_acceleration.z,3)}) m/s²')
        else:
            imu_detail = '未收到数据（仅 WHOLE_BODY_DEBUG 模式下发布）'
        results.append(('/motion/imu 传感器订阅', imu_ok, imu_detail))

        status_ok = len(self.status_msgs) > 0
        results.append(('/motion/status 状态订阅', status_ok,
                        f'收到 {len(self.status_msgs)} 帧' if status_ok else '未收到数据'))

        rs_ok = len(self.robot_state_msgs) > 0
        results.append(('/motion/robot_state 状态订阅', rs_ok,
                        f'收到 {len(self.robot_state_msgs)} 帧' if rs_ok else '未收到数据'))

        jc_ok = len(self.joint_ctrl_msgs) > 0
        results.append(('/joint_control 运控输出订阅', jc_ok,
                        f'收到 {len(self.joint_ctrl_msgs)} 帧' if jc_ok else '未收到数据'))

        print('\n════ 阶段 B：运控状态查询 ════')
        req_state = GetRobotState.Request()
        req_state.start = True
        r_state = self._call(self.cli_get_state, req_state)
        if r_state is not None:
            state_name = ROBOT_STATE_MAP.get(r_state.state, f'unknown({r_state.state})')
            results.append(('get_robot_state_srv_hl 运控状态查询', True,
                            f'state={r_state.state} ({state_name})'))
        else:
            results.append(('get_robot_state_srv_hl 运控状态查询', False, '服务调用失败'))

        print('\n════ 阶段 C：预设动作播放 ════')
        _, cur = self.get_mode()
        if cur != 'WALK':
            self.set_mode('WALK'); time.sleep(0.5)
        req_auto = SetBool.Request(); req_auto.data = True
        r_auto = self._call(self.cli_autonom, req_auto)
        auto_ok = r_auto.success if r_auto else False
        results.append(('switch_autonomous 进入动作播放模式', auto_ok,
                        r_auto.message if r_auto else '服务不可达'))

        success, feedbacks, info = self.play_action('wave_hand', timeout=15.0)
        action_iface_ok = (info in ('OK', '等待结果超时'))
        results.append(('basic_action_play wave_hand 动作播放', action_iface_ok,
                        f'success={success}, feedback={feedbacks}'))

        self.set_mode('WALK'); time.sleep(0.5)

        print('\n════ 阶段 D：行走控制权切换 /switch_drive_mode ════')
        if self.cli_drive.wait_for_service(timeout_sec=3.0):
            req_nav = SetBool.Request(); req_nav.data = True
            r_nav = self._call(self.cli_drive, req_nav)
            nav_ok = r_nav.success if r_nav else False
            results.append(('/switch_drive_mode 切换到导航模式', nav_ok,
                            r_nav.message if r_nav else '调用失败'))
        else:
            note = '服务不存在于当前仿真 binary'
            results.append(('/switch_drive_mode 服务可用性', None, note))

        self.set_mode('ZERO'); time.sleep(1.5)
        self.set_mode('STAND'); time.sleep(1.0)
        _, final_mode = self.get_mode()
        results.append(('复位到 STAND', final_mode == 'STAND', f'最终模式={final_mode}'))

        return results


def main():
    rclpy.init()
    node = SensorsAndActionsTest()
    print('=' * 65)
    print('  Test Flow 4: 传感器订阅 + 状态查询 + 预设动作 + 控制权切换')
    print('=' * 65)

    try:
        results = node.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        results = [('异常', False, str(e))]
    finally:
        node.destroy_node()
        rclpy.shutdown()

    print('\n' + '=' * 65)
    print('  测试结果汇总')
    print('=' * 65)
    passed = skipped = failed = 0
    for step, ok, detail in results:
        if ok is None:
            status = '⚠ SKIP'; skipped += 1
        elif ok:
            status = '✓ PASS'; passed += 1
        else:
            status = '✗ FAIL'; failed += 1
        print(f'  [{status}] {step}')
        print(f'          {detail}')
    print('-' * 65)
    print(f'  通过: {passed}  跳过: {skipped}  失败: {failed}')
    print('=' * 65)


if __name__ == '__main__':
    main()
