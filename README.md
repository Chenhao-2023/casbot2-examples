<a id="chinese"></a>

中文 | [English](#english)

# CASBOT2 二次开发示例仓库

本仓库用于 CASBOT2 的 ROS 2 二次开发，包含：

- 可直接运行的 C++/Python 示例工程
- 覆盖核心接口的 workflow 测试脚本
- 开机自检、仿真联调、实机联调的操作指引
- 接口全覆盖调用示例（Service / Topic / Action）

## 目录说明

- `packages/crb_ros_msg/`：ROS 2 自定义消息包（msg/srv/action）
- `examples/README.md`：示例总导航（场景、接口、workflow、基础 demo）
- `examples/cpp/casbot2_cpp_demo/`：C++ 基础 demo 包
- `examples/python/casbot2_py_demo/`：Python 基础 demo 包
- `examples/workflows/cpp/casbot_cpp_test/`：C++ workflow 测试工程（t01~t05）
- `examples/workflows/python/casbot_py_test/`：Python workflow 测试脚本（t01~t05 + test_flow）
- `examples/scenarios/`：开机自检、仿真联调、实机联调
- `examples/interfaces/README.md`：接口全覆盖说明
- `examples/interfaces/python/all_interfaces_demo.py`：全接口 Python 调用工具
- `docs/`：手册、接口、快速开始、发布说明等文档

## 环境要求

- Ubuntu 22.04
- ROS 2 Humble
- 已安装并可解析 `crb_ros_msg`

推荐环境初始化：

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## 快速开始

### 1) 运行基础 Python Demo

```bash
cd examples/python
colcon build --packages-select casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo control_demo
```

### 2) 运行 C++ Workflow Demo

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
```

### 3) 运行接口全覆盖工具

```bash
python3 examples/interfaces/python/all_interfaces_demo.py --help
```

## 安全提示

- 首次联调请从低速、小幅度关节指令开始
- 每次发控制命令前先确认当前模式
- 调试模式需有安全员在场，并确保急停可用

## 相关文档

- `docs/快速开始.md`
- `docs/二次开发手册.md`
- `docs/运动控制接口.md`
- `docs/ROS2_自定义消息包使用指南.md`
- `examples/interfaces/README.md`

---

<a id="english"></a>

[中文](#chinese) | English

# CASBOT2 Secondary Development Examples

This repository provides ROS 2 secondary development assets for CASBOT2, including:

- Runnable C++ and Python demo packages
- Workflow test scripts for core interfaces
- Scenario guides for boot check, simulation, and real robot validation
- A full interface usage toolkit (Service / Topic / Action)

## Repository Layout

- `packages/crb_ros_msg/`: ROS 2 custom interface package (`msg` / `srv` / `action`)
- `examples/README.md`: unified examples index
- `examples/cpp/casbot2_cpp_demo/`: C++ base demos
- `examples/python/casbot2_py_demo/`: Python base demos
- `examples/workflows/cpp/casbot_cpp_test/`: C++ workflow tests (t01~t05)
- `examples/workflows/python/casbot_py_test/`: Python workflow tests (t01~t05 + test_flow)
- `examples/scenarios/`: boot check / simulation / real robot operation guides
- `examples/interfaces/README.md`: full interface usage guide
- `examples/interfaces/python/all_interfaces_demo.py`: unified Python interface runner
- `docs/`: manuals, API docs, quick start, release notes

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- `crb_ros_msg` available in your ROS environment

Recommended shell initialization:

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## Quick Start

### 1) Run Python base demo

```bash
cd examples/python
colcon build --packages-select casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo control_demo
```

### 2) Run C++ workflow demo

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
```

### 3) Run full interface tool

```bash
python3 examples/interfaces/python/all_interfaces_demo.py --help
```

## Safety Notes

- Start with low speed and small joint commands
- Always confirm current robot mode before control commands
- Keep a safety operator and emergency stop ready during debug mode

## Documentation

- `docs/快速开始.md`
- `docs/二次开发手册.md`
- `docs/运动控制接口.md`
- `docs/ROS2_自定义消息包使用指南.md`
- `examples/interfaces/README.md`
