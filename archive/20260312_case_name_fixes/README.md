# 用例名称修复归档

**归档日期**: 2026-03-12
**原始位置**: `scripts/update/update_case_names.py`

## 说明

本目录归档了用例名称修复的一次性维护脚本。

## 归档原因

- 一次性维护脚本，用于修复特定创建结果的命名问题
- 硬编码了特定文件路径: `sandbox/workspace/creation_result_1772604609.json`
- 已完成其历史使命，保留作为参考

## 推荐替代方案

对于新的批量更新任务，请使用：
- `skills/sdet-skills/platform-client/` - 通过 platform_client 进行标准更新
- 遵循 `GET -> 修改 -> POST` 模式进行更新操作

## 文件清单

- `update_case_names.py` (180 lines) - 用例名称修复脚本
