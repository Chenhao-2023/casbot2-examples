<a id="chinese"></a>

中文 | [English](#english)

# 运行仿真

## 目标

在 MuJoCo 仿真环境验证模式切换、速度控制、上身调试与动作流程。

## 推荐顺序

1. 启动仿真与 `hlorin` 主进程
2. 执行开机自检（见 `boot_check.md`）
3. 运行基础控制脚本：
   - `t02_switch_mode.py`
   - `t04_cmd_vel.py`
   - `t05_upper_debug.py`
4. 运行流程测试脚本：
   - `test_flow1_walk.py`
   - `test_flow2_upper_debug.py`
   - `test_flow3_whole_body.py`
   - `test_flow4_sensors_and_actions.py`

## Python 运行示例

```bash
cd examples/workflows/python/casbot_py_test
python3 t01_get_state.py
python3 test_flow1_walk.py
```

## C++ 运行示例

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
ros2 run casbot_cpp_test t04_cmd_vel
```

## 注意事项

- 仿真分支可能与实机接口略有差异，需以当前 binary 为准。
- 部分动作在仿真下可能受限（例如腿部锁定导致动作返回失败）。


---

<a id="english"></a>

[中文](#chinese) | English

# Simulation Workflow

## Goal

Validate mode switching, velocity control, upper-body debug, and action flow in MuJoCo simulation.

## Recommended Sequence

1. Start simulation and `hlorin`
2. Run boot check (`boot_check.md`)
3. Run base control scripts:
   - `t02_switch_mode.py`
   - `t04_cmd_vel.py`
   - `t05_upper_debug.py`
4. Run flow tests:
   - `test_flow1_walk.py`
   - `test_flow2_upper_debug.py`
   - `test_flow3_whole_body.py`
   - `test_flow4_sensors_and_actions.py`

## Python Example

```bash
cd examples/workflows/python/casbot_py_test
python3 t01_get_state.py
python3 test_flow1_walk.py
```

## C++ Example

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
ros2 run casbot_cpp_test t04_cmd_vel
```

## Notes

- Simulation branch and real robot interfaces may differ; follow current binary behavior.
- Some actions can be limited in simulation (for example, leg lock causing action failure).
