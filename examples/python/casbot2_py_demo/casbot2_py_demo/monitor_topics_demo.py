import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from std_msgs.msg import String


class MonitorTopicsDemo(Node):
    def __init__(self) -> None:
        super().__init__("monitor_topics_demo")
        self.counts = {
            "/joint_states": 0,
            "/joint_control": 0,
            "/imu": 0,
            "/motion/status": 0,
            "/motion/robot_state": 0,
        }
        self.create_subscription(JointState, "/joint_states", lambda _m: self._inc("/joint_states"), 10)
        self.create_subscription(JointState, "/joint_control", lambda _m: self._inc("/joint_control"), 10)
        self.create_subscription(Imu, "/imu", lambda _m: self._inc("/imu"), 10)
        self.create_subscription(String, "/motion/status", lambda _m: self._inc("/motion/status"), 10)
        self.create_subscription(String, "/motion/robot_state", lambda _m: self._inc("/motion/robot_state"), 10)

    def _inc(self, key: str) -> None:
        self.counts[key] += 1

    def run(self, seconds: float = 5.0) -> None:
        self.get_logger().info(f"开始监听 {seconds} 秒...")
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        for topic, cnt in self.counts.items():
            self.get_logger().info(f"{topic}: {cnt}")


def main() -> None:
    rclpy.init()
    node = MonitorTopicsDemo()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
