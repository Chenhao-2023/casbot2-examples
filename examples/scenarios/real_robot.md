<a id="chinese"></a>

中文 | [English](#english)

# 运行实机测试

## 目标

按照安全顺序完成实机接口验证，覆盖模式切换、行走、上身调试和全身调试。

## 安全前提

- 周围有安全员
- 初始使用低速、低增益
- 实机已完成站立准备，急停可用

## 推荐测试流程

1. 开机自检（`boot_check.md`）
2. 模式服务检查（`t01_get_state`、`t02_switch_mode`）
3. 低速行走验证（`t04_cmd_vel`）
4. 上身调试验证（`t05_upper_debug`）
5. 全身调试验证（`test_flow3_whole_body.py`）
6. Debug 增益验证（`test_flow_debug_kp_kd.py`）

## 实机执行建议

- 先执行 Python 快速检查脚本，再执行 C++ 稳定测试程序。
- 每一阶段结束后回到 `STAND` 或 `ZERO`，再进入下一阶段。

## 典型命令

```bash
cd examples/workflows/python/casbot_py_test
python3 t01_get_state.py
python3 t02_switch_mode.py
python3 t04_cmd_vel.py
```

## 判定标准

- 服务调用成功率高
- 关节反馈连续且无异常跳变
- 模式切换符合预期，不出现不可恢复状态


---

<a id="english"></a>

[中文](#chinese) | English

# Real Robot Validation Workflow

## Goal

Complete real robot interface validation in a safe order, covering mode switching, walking, upper-body debug, and whole-body debug.

## Safety Preconditions

- Safety operator is present
- Start with low speed and low gains
- Robot is ready in standing state and emergency stop is available

## Recommended Test Flow

1. Boot check (`boot_check.md`)
2. Mode service checks (`t01_get_state`, `t02_switch_mode`)
3. Low-speed walking check (`t04_cmd_vel`)
4. Upper-body debug check (`t05_upper_debug`)
5. Whole-body debug check (`test_flow3_whole_body.py`)
6. Debug gain check (`test_flow_debug_kp_kd.py`)

## Execution Suggestions

- Run Python quick checks first, then C++ stability tests.
- Return to `STAND` or `ZERO` after each stage before entering the next stage.

## Typical Commands

```bash
cd examples/workflows/python/casbot_py_test
python3 t01_get_state.py
python3 t02_switch_mode.py
python3 t04_cmd_vel.py
```

## Pass Criteria

- High service call success rate
- Continuous joint feedback without abnormal jumps
- Mode switches behave as expected without unrecoverable state
