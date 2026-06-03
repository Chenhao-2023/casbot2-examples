<a id="chinese"></a>

中文 | [English](#english)

# 快速开始

## 1. 环境准备

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

建议按项目规范设置 `ROS_DOMAIN_ID`，并在调试时确认通信范围。

## 2. 基础检查

```bash
ros2 doctor --report
ros2 topic list
ros2 service list | grep -E "motion|robot_mode|robot_state"
```

## 3. 常用操作

- 查询模式：`get_robot_mode`
- 设置模式：`/set_robot_mode`
- 导航指令：`/navigation/cmd_vel`
- 上身调试：`/motion/upper_body_debug` + `/upper_body_debug/joint_cmd`
- 全身调试：`/motion/whole_body_debug` + `/motion/joint_cmd`
- 导航模式切换：`/motion/switch_nav_mode`

## 4. 示例运行

详见仓库根目录 `README.md` 的 C++/Python 示例运行步骤。


---

<a id="english"></a>

[中文](#chinese) | English

# Quick Start

## 1. Environment Setup

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

Set `ROS_DOMAIN_ID` according to your team rules and confirm communication scope before testing.

## 2. Basic Checks

```bash
ros2 doctor --report
ros2 topic list
ros2 service list | grep -E "motion|robot_mode|robot_state"
```

## 3. Common Operations

- Query mode: `get_robot_mode`
- Set mode: `/set_robot_mode`
- Navigation command: `/navigation/cmd_vel`
- Upper-body debug: `/motion/upper_body_debug` + `/upper_body_debug/joint_cmd`
- Whole-body debug: `/motion/whole_body_debug` + `/motion/joint_cmd`
- Navigation mode switch: `/motion/switch_nav_mode`

## 4. Run Examples

See the root `README.md` for C++ and Python run instructions.
