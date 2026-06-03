# CASBOT2 二次开发示例仓库

本仓库用于 CASBOT2 的 ROS 2 二次开发，包含：

- 可直接运行的 C++/Python 示例工程
- 覆盖核心接口的 workflow 测试脚本
- 开机自检、仿真联调、实机联调的操作指引
- 接口全覆盖调用示例（Service / Topic / Action）

## 目录说明

- `examples/cpp/casbot2_cpp_demo/`：C++ 基础 demo 包
- `examples/python/casbot2_py_demo/`：Python 基础 demo 包
- `examples/README.md`：examples 总导航
- `examples/workflows/cpp/casbot_cpp_test/`：C++ workflow 测试工程（t01~t05）
- `examples/workflows/python/casbot_py_test/`：Python workflow 测试脚本（t01~t05 + test_flow）
- `examples/scenarios/`：开机自检、仿真联调、实机联调
- `examples/interfaces/README.md`：所有接口的用法说明
- `examples/interfaces/python/all_interfaces_demo.py`：全接口 Python 调用工具
- `docs/`：对外文档（手册、接口、快速开始、发布说明）

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
- `examples/interfaces/README.md`
