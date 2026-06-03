import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import SetBool

from crb_ros_msg.msg import JointStateData


class BasicControlDemo(Node):
    def __init__(self) -> None:
        super().__init__("casbot2_py_control_demo")
        self.nav_mode_cli = self.create_client(SetBool, "/motion/switch_nav_mode")
        self.cmd_vel_pub = self.create_publisher(Twist, "/navigation/cmd_vel", 10)
        self.whole_body_pub = self.create_publisher(JointStateData, "/motion/joint_cmd", 10)

    def switch_nav_mode(self, enable_nav: bool) -> bool:
        if not self.nav_mode_cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error("Service /motion/switch_nav_mode not available")
            return False
        req = SetBool.Request()
        req.data = enable_nav
        future = self.nav_mode_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        resp = future.result()
        if resp is None:
            self.get_logger().error("Failed to call /motion/switch_nav_mode")
            return False
        target = "NAVIGATION" if enable_nav else "IDLE_MODE"
        self.get_logger().info(
            f"switch_nav_mode({target}): success={resp.success}, msg={resp.message}"
        )
        return bool(resp.success)

    def send_cmd_vel(self, vx: float, wz: float) -> None:
        msg = Twist()
        msg.linear.x = float(vx)
        msg.angular.z = float(wz)
        self.cmd_vel_pub.publish(msg)

    def send_whole_body_demo(self) -> None:
        msg = JointStateData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ["head_yaw_joint", "head_pitch_joint", "waist_yaw_joint"]
        msg.position = [0.1, -0.05, 0.0]
        msg.velocity = [0.0, 0.0, 0.0]
        msg.effort = [0.0, 0.0, 0.0]
        msg.kp = []
        msg.kd = []
        self.whole_body_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = BasicControlDemo()

    node.switch_nav_mode(True)
    for _ in range(20):
        if not rclpy.ok():
            break
        node.send_cmd_vel(0.2, 0.0)
        rclpy.spin_once(node, timeout_sec=0.05)
        time.sleep(0.1)
    node.switch_nav_mode(False)

    node.send_whole_body_demo()
    rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
