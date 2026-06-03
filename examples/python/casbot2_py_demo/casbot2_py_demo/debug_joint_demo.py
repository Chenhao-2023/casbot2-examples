import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

from crb_ros_msg.msg import JointStateData, UpperJointData


class DebugJointDemo(Node):
    def __init__(self) -> None:
        super().__init__("debug_joint_demo")
        self.upper_debug_cli = self.create_client(SetBool, "/motion/upper_body_debug")
        self.whole_debug_cli = self.create_client(SetBool, "/motion/whole_body_debug")
        self.upper_pub = self.create_publisher(UpperJointData, "/upper_body_debug/joint_cmd", 10)
        self.whole_pub = self.create_publisher(JointStateData, "/motion/joint_cmd", 10)

    def call_set_bool(self, cli, enable: bool) -> bool:
        if not cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error(f"服务不可用: {cli.srv_name}")
            return False
        req = SetBool.Request()
        req.data = enable
        fut = cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=3.0)
        resp = fut.result()
        if resp:
            self.get_logger().info(
                f"{cli.srv_name}({enable}) => success={resp.success}, msg={resp.message}"
            )
            return bool(resp.success)
        return False

    def run(self) -> None:
        self.call_set_bool(self.upper_debug_cli, True)
        upper = UpperJointData()
        upper.header.stamp = self.get_clock().now().to_msg()
        upper.time_ref = 0.0
        upper.vel_scale = 0.05
        upper.joint.name = ["left_shoulder_pitch_joint", "right_shoulder_pitch_joint"]
        upper.joint.position = [0.05, 0.05]
        upper.joint.velocity = [0.0, 0.0]
        upper.joint.effort = [0.0, 0.0]
        self.upper_pub.publish(upper)
        self.get_logger().info("已发送 upper_body_debug 关节命令")
        self.call_set_bool(self.upper_debug_cli, False)

        self.call_set_bool(self.whole_debug_cli, True)
        whole = JointStateData()
        whole.header.stamp = self.get_clock().now().to_msg()
        whole.name = ["head_yaw_joint", "head_pitch_joint", "waist_yaw_joint"]
        whole.position = [0.1, -0.05, 0.0]
        whole.velocity = [0.0, 0.0, 0.0]
        whole.effort = [0.0, 0.0, 0.0]
        whole.kp = []
        whole.kd = []
        self.whole_pub.publish(whole)
        self.get_logger().info("已发送 whole_body_debug 关节命令")
        self.call_set_bool(self.whole_debug_cli, False)


def main() -> None:
    rclpy.init()
    node = DebugJointDemo()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
