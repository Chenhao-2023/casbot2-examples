import json

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from crb_ros_msg.action import BasicActionPlay, VoicePlay
from crb_ros_msg.srv import ActionEvent, Voice


class ActionVoiceDemo(Node):
    def __init__(self) -> None:
        super().__init__("action_voice_demo")
        self.event_cli = self.create_client(ActionEvent, "/casbot/event_service")
        self.voice_cli = self.create_client(Voice, "/voice_svr")
        self.basic_action_cli = ActionClient(self, BasicActionPlay, "/basic_action_play")
        self.voice_action_cli = ActionClient(self, VoicePlay, "/action_voice_play")

    def call_service(self, cli, req, timeout_sec=3.0):
        if not cli.wait_for_service(timeout_sec=timeout_sec):
            self.get_logger().warn(f"服务不可用: {cli.srv_name}")
            return None
        fut = cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=timeout_sec)
        return fut.result()

    def run(self) -> None:
        event_req = ActionEvent.Request()
        event_req.event_id = ""
        event_req.event_type = "ExecSkill"
        event_req.blocking = False
        event_req.param_json = json.dumps(
            {
                "payload": json.dumps({"action_type": "wave_hand"}),
                "target_tree": "basic_action_play",
            }
        )
        event_resp = self.call_service(self.event_cli, event_req)
        if event_resp:
            self.get_logger().info(
                f"event_service: success={event_resp.success}, msg={event_resp.message}"
            )

        voice_req = Voice.Request()
        voice_req.type = "question"
        voice_req.content_type = "text"
        voice_req.content = "你好"
        voice_resp = self.call_service(self.voice_cli, voice_req)
        if voice_resp:
            self.get_logger().info(f"voice_svr: success={voice_resp.success}")

        if self.basic_action_cli.wait_for_server(timeout_sec=2.0):
            goal = BasicActionPlay.Goal()
            goal.type = "wave_hand"
            fut = self.basic_action_cli.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, fut, timeout_sec=3.0)
            self.get_logger().info("basic_action_play goal sent")
        else:
            self.get_logger().warn("basic_action_play action 不可用")

        if self.voice_action_cli.wait_for_server(timeout_sec=2.0):
            goal = VoicePlay.Goal()
            goal.wav_path = "test.wav"
            fut = self.voice_action_cli.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, fut, timeout_sec=3.0)
            self.get_logger().info("voice_play goal sent")
        else:
            self.get_logger().warn("action_voice_play action 不可用")


def main() -> None:
    rclpy.init()
    node = ActionVoiceDemo()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
