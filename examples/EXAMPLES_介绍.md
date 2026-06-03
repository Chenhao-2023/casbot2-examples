# CASBOT2 Examples 说明

本目录用于集中管理 CASBOT2 二次开发示例，分为 4 类：

1. 开机自检
2. 运行仿真
3. 运行实机测试
4. C++ / Python workflow 示例

## 目录结构

- `00_开机自检.md`：上电后自检与 ROS 接口连通性检查
- `01_运行仿真.md`：MuJoCo 仿真环境下的推荐运行流程
- `02_运行实机测试.md`：实机模式下的安全测试顺序
- `接口全覆盖示例.md`：按接口逐项给出调用用法
- `interfaces/python/all_interfaces_demo.py`：全接口统一调用脚本
- `workflows/cpp/casbot_cpp_test/`：C++ 版本 workflow
- `workflows/python/casbot_py_test/`：Python 版本 workflow

## 使用建议

- 先执行 `00_开机自检.md`，确认服务与话题可用。
- 再按场景选择：
  - 仿真：`01_运行仿真.md`
  - 实机：`02_运行实机测试.md`
- 需要自动化验证时，直接运行 `workflows` 内脚本。

## 说明

- `workflows` 中内容来自：
  - `/home/robotch/work/casbot_cpp_test`
  - `/home/robotch/work/casbot_py_test`
- 脚本按当前收集版本原样整理，若接口升级请同步更新。
