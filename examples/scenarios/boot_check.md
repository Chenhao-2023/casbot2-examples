<a id="chinese"></a>

中文 | [English](#english)

# 开机自检

## 目标

确认机器人或仿真进程启动后，ROS 2 通道、关键服务和关键话题全部可用。

## 步骤

1. Source 环境

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

2. 基础诊断

```bash
ros2 doctor --report
ros2 topic list
ros2 service list
```

3. 核心接口检查

```bash
ros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode "{}"
ros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState "{start: true}"
ros2 topic info /joint_states
ros2 topic info /navigation/cmd_vel
```

4. 建议执行 workflow 自检脚本

- Python：`../workflows/python/casbot_py_test/t01_get_state.py`
- C++：`../workflows/cpp/casbot_cpp_test/src/t01_get_state.cpp`（先编译）

## 判定标准

- 核心服务调用返回正常
- `/joint_states` 有持续数据
- 模式切换服务可用且返回成功


---

<a id="english"></a>

[中文](#chinese) | English

# Boot Check

## Goal

After robot or simulation startup, confirm ROS 2 communication, key services, and key topics are all available.

## Steps

1. Source environment

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

2. Basic diagnostics

```bash
ros2 doctor --report
ros2 topic list
ros2 service list
```

3. Core interface checks

```bash
ros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode "{}"
ros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState "{start: true}"
ros2 topic info /joint_states
ros2 topic info /navigation/cmd_vel
```

4. Recommended workflow self-check scripts

- Python: `../workflows/python/casbot_py_test/t01_get_state.py`
- C++: `../workflows/cpp/casbot_cpp_test/src/t01_get_state.cpp` (build first)

## Pass Criteria

- Core service calls return successfully
- `/joint_states` has continuous data
- Mode-switch services are available and return success
