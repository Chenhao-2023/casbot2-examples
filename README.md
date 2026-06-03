# CASBOT2 Secondary Development

CASBOT2 secondary development examples and documentation based on ROS 2 Humble.

## Repository Layout

- `examples/cpp/casbot2_cpp_demo/`: C++ ROS 2 demo package
- `examples/python/casbot2_py_demo/`: Python ROS 2 demo package
- `examples/EXAMPLES_介绍.md`: examples 总览（含开机自检/仿真/实机/workflow）
- `examples/workflows/cpp/casbot_cpp_test/`: C++ workflow 工程
- `examples/workflows/python/casbot_py_test/`: Python workflow 脚本
- `docs/`: quick start and API documents

## Environment

- Ubuntu 22.04
- ROS 2 Humble
- `crb_ros_msg` installed in your ROS environment

Recommended shell setup:

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## Build and Run

### C++ demo package

```bash
cd examples/cpp
colcon build --packages-select casbot2_cpp_demo
source install/setup.bash
ros2 run casbot2_cpp_demo basic_control_demo
```

### Python demo package

```bash
cd examples/python
colcon build --packages-select casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo control_demo
```

## Safety Notice

- Always start with low speed and low gain.
- Confirm robot mode before sending control command.
- Use test support and safety supervision in debug mode.

## Related Docs

- `docs/快速开始.md`
- `docs/二次开发手册.md`
- `docs/运动控制接口.md`
- `docs/发布说明.md`
