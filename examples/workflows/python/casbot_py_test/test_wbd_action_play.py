#!/usr/bin/env python3
"""
测试：全身调试模式（WHOLE_BODY_DEBUG）下能否播放上身技能（ACTION_PLAY）
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_srvs.srv import SetBool
from crb_ros_msg.srv import SetRobotMode, GetRobotMode
from crb_ros_msg.action import BasicActionPlay
import time


class WbdActionPlayTest(Node):
    def __init__(self):
        super().__init__('wbd_action_play_test')
        self.cli_set_mode = self.create_client(SetRobotMode, '/set_robot_mode')
        self.cli_get_mode = self.create_client(GetRobotMode, '/get_robot_mode')
        self.cli_autonom = self.create_client(SetBool, 'switch_autonomous')
        self.cli_debug = self.create_client(SetBool, '/motion/whole_body_debug')
        self.action_cli = ActionClient(self, BasicActionPlay, '/basic_action_play')

    def _call(self, client, req, timeout=5.0):
        if not client.wait_for_service(timeout_sec=timeout):
            return None
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        return future.result() if future.done() else None

    def get_mode(self):
        r = self._call(self.cli_get_mode, GetRobotMode.Request())
        return (r.mode, r.mode_name) if r else (-1, '?')

    def set_mode(self, mode_name: str) -> bool:
        req = SetRobotMode.Request()
        req.mode_name = mode_name
        r = self._call(self.cli_set_mode, req)
        return r.success if r else False

    def try_action(self, action_type: str, timeout: float = 8.0):
        if not self.action_cli.wait_for_server(timeout_sec=5.0):
            return False, 'action server not available'
        goal = BasicActionPlay.Goal()
        goal.type = action_type
        future = self.action_cli.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        gh = future.result() if future.done() else None
        if gh is None or not gh.accepted:
            return False, 'goal rejected'
        result_future = gh.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=timeout)
        if result_future.done():
            r = result_future.result()
            return True, r.result.if_success
        return True, 'timeout'

    def run(self):
        req_in = SetBool.Request(); req_in.data = True
        r = self._call(self.cli_debug, req_in)
        print('进入WHOLE_BODY_DEBUG:', r.success if r else False, r.message if r else '')

        req_sw = SetBool.Request(); req_sw.data = True
        r2 = self._call(self.cli_autonom, req_sw)
        print('switch_autonomous(true):', r2.success if r2 else False, r2.message if r2 else '')

        accepted, action_result = self.try_action('wave_hand', timeout=8.0)
        print('basic_action_play:', accepted, action_result)

        req_out = SetBool.Request(); req_out.data = False
        self._call(self.cli_debug, req_out)
        self.set_mode('STAND')


def main():
    rclpy.init()
    node = WbdActionPlayTest()
    time.sleep(1.0)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
