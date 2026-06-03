import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

from crb_ros_msg.srv import GetRobotMode, GetRobotState, SetRobotMode


class ServiceModeDemo(Node):
    def __init__(self) -> None:
        super().__init__("service_mode_demo")
        self.get_mode_cli = self.create_client(GetRobotMode, "get_robot_mode")
        self.set_mode_cli = self.create_client(SetRobotMode, "/set_robot_mode")
        self.get_state_cli = self.create_client(GetRobotState, "get_robot_state_srv_hl")
        self.nav_cli = self.create_client(SetBool, "/motion/switch_nav_mode")
        self.teleop_cli = self.create_client(SetBool, "/switch_teleoperation")
        self.auto_cli = self.create_client(SetBool, "/switch_autonomous")

    def call(self, cli, req, timeout_sec=3.0):
        if not cli.wait_for_service(timeout_sec=timeout_sec):
            self.get_logger().error(f"服务不可用: {cli.srv_name}")
            return None
        fut = cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=timeout_sec)
        return fut.result()

    def run(self) -> None:
        mode = self.call(self.get_mode_cli, GetRobotMode.Request())
        if mode:
            self.get_logger().info(f"当前模式: mode={mode.mode}, mode_name={mode.mode_name}")

        state_req = GetRobotState.Request()
        state_req.start = True
        state = self.call(self.get_state_cli, state_req)
        if state:
            self.get_logger().info(f"机器人状态: state={state.state}")

        set_req = SetRobotMode.Request()
        set_req.mode_name = "WALK"
        set_resp = self.call(self.set_mode_cli, set_req)
        if set_resp:
            self.get_logger().info(f"set_robot_mode(WALK): {set_resp.success}")

        for name, cli, enable in [
            ("switch_nav_mode", self.nav_cli, True),
            ("switch_nav_mode", self.nav_cli, False),
            ("switch_teleoperation", self.teleop_cli, True),
            ("switch_teleoperation", self.teleop_cli, False),
            ("switch_autonomous", self.auto_cli, True),
            ("switch_autonomous", self.auto_cli, False),
        ]:
            req = SetBool.Request()
            req.data = enable
            resp = self.call(cli, req)
            if resp:
                self.get_logger().info(
                    f"{name}({enable}) => success={resp.success}, msg={resp.message}"
                )


def main() -> None:
    rclpy.init()
    node = ServiceModeDemo()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
