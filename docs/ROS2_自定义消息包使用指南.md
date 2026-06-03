<a id="chinese"></a>

中文 | [English](#english)

# ROS 2 自定义消息包使用指南（`crb_ros_msg`）

本仓库已内置 CASBOT2 使用的自定义消息包：

- 路径：`packages/crb_ros_msg`
- 包名：`crb_ros_msg`
- 类型覆盖：`msg` / `srv` / `action`

## 1. 目录结构

`crb_ros_msg` 主要内容：

- `msg/`：自定义消息（如 `UpperJointData.msg`、`RobotState.msg`）
- `srv/`：服务接口（如 `GetRobotMode.srv`、`SetRobotMode.srv`、`Voice.srv`）
- `action/`：动作接口（如 `BasicActionPlay.action`、`VoicePlay` 对应动作）
- `CMakeLists.txt`：`rosidl_generate_interfaces(...)` 生成入口
- `package.xml`：依赖声明（`rosidl_default_generators`、`std_msgs`、`sensor_msgs`）

## 2. 如何编译这个自定义消息包

在仓库根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
```

验证：

```bash
ros2 interface list | grep crb_ros_msg
ros2 interface show crb_ros_msg/msg/UpperJointData
ros2 interface show crb_ros_msg/srv/GetRobotMode
ros2 interface show crb_ros_msg/action/BasicActionPlay
```

## 3. 在 Python 包中使用

`package.xml` 需要声明依赖：

```xml
<depend>crb_ros_msg</depend>
```

代码导入示例：

```python
from crb_ros_msg.msg import JointStateData
from crb_ros_msg.srv import GetRobotMode
from crb_ros_msg.action import BasicActionPlay
```

## 4. 在 C++ 包中使用

`package.xml` 需要声明依赖：

```xml
<depend>crb_ros_msg</depend>
```

`CMakeLists.txt` 需要：

```cmake
find_package(crb_ros_msg REQUIRED)
ament_target_dependencies(your_target crb_ros_msg)
```

代码包含示例：

```cpp
#include "crb_ros_msg/msg/joint_state_data.hpp"
#include "crb_ros_msg/srv/get_robot_mode.hpp"
#include "crb_ros_msg/action/basic_action_play.hpp"
```

## 5. 常见问题

- **Q: `ModuleNotFoundError: crb_ros_msg`（Python）**  
  A: 没有 `source install/setup.bash`，或 `crb_ros_msg` 未编译成功。

- **Q: C++ 找不到头文件**  
  A: 检查 `find_package(crb_ros_msg REQUIRED)` 和 `ament_target_dependencies(...)` 是否已添加。

- **Q: `ros2 interface show` 查不到接口**  
  A: 当前终端环境未 source 正确工作区，或消息包编译失败。


---

<a id="english"></a>

[中文](#chinese) | English

# ROS 2 Custom Interface Package Guide (`crb_ros_msg`)

This repository already includes the custom interface package used by CASBOT2:

- Path: `packages/crb_ros_msg`
- Package name: `crb_ros_msg`
- Interface types: `msg` / `srv` / `action`

## 1. Package Structure

Main contents of `crb_ros_msg`:

- `msg/`: custom messages (for example, `UpperJointData.msg`, `RobotState.msg`)
- `srv/`: service definitions (for example, `GetRobotMode.srv`, `SetRobotMode.srv`, `Voice.srv`)
- `action/`: action definitions (for example, `BasicActionPlay.action`)
- `CMakeLists.txt`: `rosidl_generate_interfaces(...)` entry
- `package.xml`: dependency declarations (`rosidl_default_generators`, `std_msgs`, `sensor_msgs`)

## 2. Build the Custom Package

Run at repository root:

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
```

Verify interfaces:

```bash
ros2 interface list | grep crb_ros_msg
ros2 interface show crb_ros_msg/msg/UpperJointData
ros2 interface show crb_ros_msg/srv/GetRobotMode
ros2 interface show crb_ros_msg/action/BasicActionPlay
```

## 3. Use in Python Packages

Add dependency in `package.xml`:

```xml
<depend>crb_ros_msg</depend>
```

Python imports:

```python
from crb_ros_msg.msg import JointStateData
from crb_ros_msg.srv import GetRobotMode
from crb_ros_msg.action import BasicActionPlay
```

## 4. Use in C++ Packages

Add dependency in `package.xml`:

```xml
<depend>crb_ros_msg</depend>
```

In `CMakeLists.txt`:

```cmake
find_package(crb_ros_msg REQUIRED)
ament_target_dependencies(your_target crb_ros_msg)
```

C++ headers:

```cpp
#include "crb_ros_msg/msg/joint_state_data.hpp"
#include "crb_ros_msg/srv/get_robot_mode.hpp"
#include "crb_ros_msg/action/basic_action_play.hpp"
```

## 5. FAQ

- **Q: `ModuleNotFoundError: crb_ros_msg` in Python**  
  A: `install/setup.bash` is not sourced, or `crb_ros_msg` has not been built correctly.

- **Q: C++ cannot find message headers**  
  A: Check both `find_package(crb_ros_msg REQUIRED)` and `ament_target_dependencies(...)`.

- **Q: `ros2 interface show` cannot find interfaces**  
  A: Current terminal environment is not sourced correctly, or message package build failed.
