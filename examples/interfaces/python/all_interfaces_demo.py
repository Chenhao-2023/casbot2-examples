#!/usr/bin/env python3
import argparse
import json
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState, Imu
from std_msgs.msg import String
from std_srvs.srv import SetBool

from crb_ros_msg.action import BasicActionPlay, VoicePlay
from crb_ros_msg.msg import UpperJointData, JointStateData
from crb_ros_msg.srv import (
    ActionEvent,
    GetRobotMode,
    GetRobotState,
    SetRobotMode,
    Voice,
)


def parse_bool(v: str) -> bool:
    return str(v).lower() in ("1", "true", "yes", "y", "on")


def parse_csv_str(s: str):
    return [x.strip() for x in s.split(",") if x.strip()]


def parse_csv_float(s: str):
    return [float(x.strip()) for x in s.split(",") if x.strip()]


class InterfaceDemo(Node):
    def __init__(self):
        super().__init__("all_interfaces_demo")

    def call_service(self, srv_type, name, req, timeout=5.0):
        cli = self.create_client(srv_type, name)
        if not cli.wait_for_service(timeout_sec=timeout):
            self.get_logger().error(f"服务不可用: {name}")
            return None
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        return future.result() if future.done() else None

    def cmd_get_robot_mode(self):
        resp = self.call_service(GetRobotMode, "get_robot_mode", GetRobotMode.Request())
        if resp:
            print(f"mode={resp.mode}, mode_name={resp.mode_name}")

    def cmd_set_robot_mode(self, mode: str):
        req = SetRobotMode.Request()
        req.mode_name = mode
        resp = self.call_service(SetRobotMode, "/set_robot_mode", req)
        if resp:
            print(f"success={resp.success}")

    def cmd_get_robot_state(self):
        req = GetRobotState.Request()
        req.start = True
        resp = self.call_service(GetRobotState, "get_robot_state_srv_hl", req)
        if resp:
            print(f"state={resp.state}")

    def cmd_switch_bool(self, srv_name: str, enable: bool):
        req = SetBool.Request()
        req.data = enable
        resp = self.call_service(SetBool, srv_name, req)
        if resp:
            print(f"{srv_name}: success={resp.success}, message={resp.message}")

    def cmd_pub_cmd_vel(self, vx: float, wz: float, seconds: float, hz: float):
        pub = self.create_publisher(Twist, "/navigation/cmd_vel", 10)
        period = 1.0 / hz if hz > 0 else 0.1
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            msg = Twist()
            msg.linear.x = vx
            msg.angular.z = wz
            pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(period)
        pub.publish(Twist())
        print("cmd_vel 已发送并停止")

    def cmd_pub_upper(self, names, positions, vel_scale=0.05):
        if len(names) != len(positions):
            raise ValueError("names 与 positions 长度不一致")
        pub = self.create_publisher(UpperJointData, "/upper_body_debug/joint_cmd", 10)
        msg = UpperJointData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.time_ref = 0.0
        msg.vel_scale = float(vel_scale)
        msg.joint.name = names
        msg.joint.position = positions
        msg.joint.velocity = [0.0] * len(names)
        msg.joint.effort = [0.0] * len(names)
        pub.publish(msg)
        rclpy.spin_once(self, timeout_sec=0.05)
        print("upper joint cmd 已发送")

    def cmd_pub_whole(self, names, positions, kp=None, kd=None):
        if len(names) != len(positions):
            raise ValueError("names 与 positions 长度不一致")
        pub = self.create_publisher(JointStateData, "/motion/joint_cmd", 10)
        msg = JointStateData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        msg.velocity = [0.0] * len(names)
        msg.effort = [0.0] * len(names)
        msg.kp = kp if kp else []
        msg.kd = kd if kd else []
        pub.publish(msg)
        rclpy.spin_once(self, timeout_sec=0.05)
        print("whole joint cmd 已发送")

    def cmd_sub_topic(self, msg_type, topic: str, seconds: float):
        count = {"n": 0}

        def cb(_msg):
            count["n"] += 1

        self.create_subscription(msg_type, topic, cb, 10)
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        print(f"{topic} 收到消息: {count['n']} 条")

    def cmd_sub_status(self, seconds: float):
        status = {"motion_status": 0, "robot_state": 0}
        self.create_subscription(String, "/motion/status", lambda _m: status.__setitem__("motion_status", status["motion_status"] + 1), 10)
        self.create_subscription(String, "/motion/robot_state", lambda _m: status.__setitem__("robot_state", status["robot_state"] + 1), 10)
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        print(f"/motion/status={status['motion_status']}, /motion/robot_state={status['robot_state']}")

    def cmd_basic_action_play(self, action_type: str):
        client = ActionClient(self, BasicActionPlay, "/basic_action_play")
        if not client.wait_for_server(timeout_sec=5.0):
            print("basic_action_play action 不可用")
            return
        goal = BasicActionPlay.Goal()
        goal.type = action_type
        send_future = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=5.0)
        if not send_future.done() or not send_future.result().accepted:
            print("goal 未被接受")
            return
        result_future = send_future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=20.0)
        if result_future.done():
            print(f"basic_action_play result: {result_future.result().result.if_success}")

    def cmd_voice_service(self, t: str, content_type: str, content: str):
        req = Voice.Request()
        req.type = t
        req.content_type = content_type
        req.content = content
        resp = self.call_service(Voice, "/voice_svr", req)
        if resp:
            print(f"voice_svr success={resp.success}, result={resp.result}")

    def cmd_voice_play(self, wav: str):
        client = ActionClient(self, VoicePlay, "/action_voice_play")
        if not client.wait_for_server(timeout_sec=5.0):
            print("action_voice_play 不可用")
            return
        goal = VoicePlay.Goal()
        goal.wav_path = wav
        send_future = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=5.0)
        if not send_future.done() or not send_future.result().accepted:
            print("voice play goal 未被接受")
            return
        result_future = send_future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=20.0)
        print("voice play 已完成")

    def cmd_event_skill(self, action_type: str, blocking: bool):
        req = ActionEvent.Request()
        req.event_id = ""
        req.event_type = "ExecSkill"
        req.blocking = blocking
        req.param_json = json.dumps(
            {
                "payload": json.dumps({"action_type": action_type}),
                "target_tree": "basic_action_play",
            }
        )
        resp = self.call_service(ActionEvent, "/casbot/event_service", req)
        if resp:
            print(f"event_service success={resp.success}, message={resp.message}")


def build_parser():
    p = argparse.ArgumentParser(description="CASBOT2 全接口示例工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("get_robot_mode")
    s = sub.add_parser("set_robot_mode")
    s.add_argument("--mode", required=True, choices=["ZERO", "STAND", "WALK"])
    sub.add_parser("get_robot_state")

    s = sub.add_parser("switch_nav_mode")
    s.add_argument("--enable", required=True)
    s = sub.add_parser("switch_teleoperation")
    s.add_argument("--enable", required=True)
    s = sub.add_parser("switch_autonomous")
    s.add_argument("--enable", required=True)
    s = sub.add_parser("upper_body_debug")
    s.add_argument("--enable", required=True)
    s = sub.add_parser("whole_body_debug")
    s.add_argument("--enable", required=True)

    s = sub.add_parser("pub_cmd_vel")
    s.add_argument("--vx", type=float, default=0.2)
    s.add_argument("--wz", type=float, default=0.0)
    s.add_argument("--seconds", type=float, default=2.0)
    s.add_argument("--hz", type=float, default=10.0)

    s = sub.add_parser("pub_upper_cmd")
    s.add_argument("--names", required=True)
    s.add_argument("--positions", required=True)
    s.add_argument("--vel-scale", type=float, default=0.05)

    s = sub.add_parser("pub_whole_cmd")
    s.add_argument("--names", required=True)
    s.add_argument("--positions", required=True)
    s.add_argument("--kp", default="")
    s.add_argument("--kd", default="")

    s = sub.add_parser("sub_motion_joint_state")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_joint_states")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_joint_control")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_status")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_imu")
    s.add_argument("--topic", default="/imu")
    s.add_argument("--seconds", type=float, default=3.0)

    s = sub.add_parser("basic_action_play")
    s.add_argument("--type", default="wave_hand")

    s = sub.add_parser("voice_service")
    s.add_argument("--type", required=True)
    s.add_argument("--content-type", default="")
    s.add_argument("--content", default="")

    s = sub.add_parser("voice_play")
    s.add_argument("--wav", required=True)

    s = sub.add_parser("event_skill")
    s.add_argument("--action-type", default="wave_hand")
    s.add_argument("--blocking", default="false")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    rclpy.init()
    node = InterfaceDemo()
    try:
        if args.cmd == "get_robot_mode":
            node.cmd_get_robot_mode()
        elif args.cmd == "set_robot_mode":
            node.cmd_set_robot_mode(args.mode)
        elif args.cmd == "get_robot_state":
            node.cmd_get_robot_state()
        elif args.cmd == "switch_nav_mode":
            node.cmd_switch_bool("/motion/switch_nav_mode", parse_bool(args.enable))
        elif args.cmd == "switch_teleoperation":
            node.cmd_switch_bool("/switch_teleoperation", parse_bool(args.enable))
        elif args.cmd == "switch_autonomous":
            node.cmd_switch_bool("/switch_autonomous", parse_bool(args.enable))
        elif args.cmd == "upper_body_debug":
            node.cmd_switch_bool("/motion/upper_body_debug", parse_bool(args.enable))
        elif args.cmd == "whole_body_debug":
            node.cmd_switch_bool("/motion/whole_body_debug", parse_bool(args.enable))
        elif args.cmd == "pub_cmd_vel":
            node.cmd_pub_cmd_vel(args.vx, args.wz, args.seconds, args.hz)
        elif args.cmd == "pub_upper_cmd":
            node.cmd_pub_upper(parse_csv_str(args.names), parse_csv_float(args.positions), args.vel_scale)
        elif args.cmd == "pub_whole_cmd":
            kp = parse_csv_float(args.kp) if args.kp else []
            kd = parse_csv_float(args.kd) if args.kd else []
            node.cmd_pub_whole(parse_csv_str(args.names), parse_csv_float(args.positions), kp, kd)
        elif args.cmd == "sub_motion_joint_state":
            node.cmd_sub_topic(JointStateData, "/motion/joint_state", args.seconds)
        elif args.cmd == "sub_joint_states":
            node.cmd_sub_topic(JointState, "/joint_states", args.seconds)
        elif args.cmd == "sub_joint_control":
            node.cmd_sub_topic(JointState, "/joint_control", args.seconds)
        elif args.cmd == "sub_status":
            node.cmd_sub_status(args.seconds)
        elif args.cmd == "sub_imu":
            node.cmd_sub_topic(Imu, args.topic, args.seconds)
        elif args.cmd == "basic_action_play":
            node.cmd_basic_action_play(args.type)
        elif args.cmd == "voice_service":
            node.cmd_voice_service(args.type, args.content_type, args.content)
        elif args.cmd == "voice_play":
            node.cmd_voice_play(args.wav)
        elif args.cmd == "event_skill":
            node.cmd_event_skill(args.action_type, parse_bool(args.blocking))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
