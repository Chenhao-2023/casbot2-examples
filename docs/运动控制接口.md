<a id="chinese"></a>

中文 | [English](#english)

# CASBOT2 ROS 2 运动控制接口（发布版）

## 接口总览

| 类型 | 名称 | 类型 |
|------|------|------|
| Service | `get_robot_mode` | `crb_ros_msg/srv/GetRobotMode` |
| Service | `/set_robot_mode` | `crb_ros_msg/srv/SetRobotMode` |
| Service | `/motion/upper_body_debug` | `std_srvs/srv/SetBool` |
| Service | `/motion/whole_body_debug` | `std_srvs/srv/SetBool` |
| Service | `/motion/switch_nav_mode` | `std_srvs/srv/SetBool` |
| Topic | `/navigation/cmd_vel` | `geometry_msgs/msg/Twist` |
| Topic | `/upper_body_debug/joint_cmd` | `crb_ros_msg/msg/UpperJointData` |
| Topic | `/motion/joint_cmd` | `crb_ros_msg/msg/JointStateData` |
| Topic | `/motion/joint_state` | `crb_ros_msg/msg/JointStateData` |

## 全身调试接口说明

- 打开调试：`/motion/whole_body_debug`，`data=true`
- 控制指令：`/motion/joint_cmd`
- 状态反馈：`/motion/joint_state`
- 调试增益：
  - `use_default_kp_kd=true` 时可不下发 `kp/kd`
  - `use_default_kp_kd=false` 时需按关节下发 `kp/kd`

## 导航模式开关

- Service：`/motion/switch_nav_mode`
- `data=true`：切换到 `NAVIGATION`
- `data=false`：退出导航，回到 `IDLE_MODE`

## 安全建议

- 先确认当前模式，再发控制指令；
- 首次联调使用小幅关节命令；
- 及时监控服务返回与状态反馈话题。


---

<a id="english"></a>

[中文](#chinese) | English

# CASBOT2 ROS 2 Motion Control Interfaces (Release Edition)

## Interface Overview

| Type | Name | Interface Type |
|------|------|----------------|
| Service | `get_robot_mode` | `crb_ros_msg/srv/GetRobotMode` |
| Service | `/set_robot_mode` | `crb_ros_msg/srv/SetRobotMode` |
| Service | `/motion/upper_body_debug` | `std_srvs/srv/SetBool` |
| Service | `/motion/whole_body_debug` | `std_srvs/srv/SetBool` |
| Service | `/motion/switch_nav_mode` | `std_srvs/srv/SetBool` |
| Topic | `/navigation/cmd_vel` | `geometry_msgs/msg/Twist` |
| Topic | `/upper_body_debug/joint_cmd` | `crb_ros_msg/msg/UpperJointData` |
| Topic | `/motion/joint_cmd` | `crb_ros_msg/msg/JointStateData` |
| Topic | `/motion/joint_state` | `crb_ros_msg/msg/JointStateData` |

## Whole-Body Debug Interface Notes

- Enable debug mode: `/motion/whole_body_debug`, `data=true`
- Control command: `/motion/joint_cmd`
- State feedback: `/motion/joint_state`
- Gain rules:
  - If `use_default_kp_kd=true`, `kp/kd` can be omitted
  - If `use_default_kp_kd=false`, `kp/kd` must be provided per controlled joint

## Navigation Mode Switch

- Service: `/motion/switch_nav_mode`
- `data=true`: switch to `NAVIGATION`
- `data=false`: exit navigation and return to `IDLE_MODE`

## Safety Recommendations

- Confirm current mode before sending control commands
- Use small joint commands for first-time tuning
- Monitor both service responses and state feedback topics
