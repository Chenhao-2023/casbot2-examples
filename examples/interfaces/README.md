# 接口全覆盖示例

本文档给出 CASBOT2 常用接口的“可执行示例入口”。  
配套脚本：`python/all_interfaces_demo.py`

## 使用前准备

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## 1. 模式与状态类 Service

- `get_robot_mode`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py get_robot_mode
  ```
- `/set_robot_mode`（`ZERO`/`STAND`/`WALK`）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py set_robot_mode --mode WALK
  ```
- `get_robot_state_srv_hl`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py get_robot_state
  ```
- `/motion/switch_nav_mode`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py switch_nav_mode --enable true
  ```
- `/switch_teleoperation`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py switch_teleoperation --enable true
  ```
- `/switch_autonomous`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py switch_autonomous --enable true
  ```
- `/motion/upper_body_debug`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py upper_body_debug --enable true
  ```
- `/motion/whole_body_debug`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py whole_body_debug --enable true
  ```

## 2. 控制类 Topic

- `/navigation/cmd_vel`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py pub_cmd_vel --vx 0.2 --wz 0.0 --seconds 2
  ```
- `/upper_body_debug/joint_cmd` (`UpperJointData`)
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py pub_upper_cmd \
    --names left_shoulder_pitch_joint,right_shoulder_pitch_joint \
    --positions 0.05,0.05 --vel-scale 0.05
  ```
- `/motion/joint_cmd` (`JointStateData`)
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py pub_whole_cmd \
    --names head_yaw_joint,head_pitch_joint \
    --positions 0.1,-0.05
  ```

## 3. 订阅类 Topic

- `/motion/joint_state`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py sub_motion_joint_state --seconds 3
  ```
- `/joint_states`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py sub_joint_states --seconds 3
  ```
- `/joint_control`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py sub_joint_control --seconds 3
  ```
- `/motion/status` + `/motion/robot_state`
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py sub_status --seconds 3
  ```
- `/imu`（或 `/motion/imu`）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py sub_imu --topic /imu --seconds 3
  ```

## 4. 动作与应用接口

- `basic_action_play`（`BasicActionPlay`）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py basic_action_play --type wave_hand
  ```
- `/voice_svr`（`Voice` Service）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py voice_service --type rtc_start
  python3 examples/interfaces/python/all_interfaces_demo.py voice_service --type question --content "你好"
  ```
- `/action_voice_play`（`VoicePlay` Action）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py voice_play --wav test.wav
  ```
- `/casbot/event_service`（`ActionEvent`）
  ```bash
  python3 examples/interfaces/python/all_interfaces_demo.py event_skill --action-type wave_hand
  ```
