# 脚本使用指南

本目录存放可直接执行的脚本，用于批量操作、自动化任务等。

## 📁 目录结构

```
scripts/
├── create/      # 创建类脚本
├── update/      # 更新类脚本
├── sync/        # 同步类脚本
└── utils/       # 脚本通用工具
```

## 🚀 快速使用

### 创建类脚本

#### 批量创建目录和用例
```bash
python scripts/create/create_directories_and_cases.py
```

**功能**：
- 在SDET平台创建目录结构
- 创建自动化用例
- 支持按配置状态分类

**输出**：
- 创建结果：`sandbox/workspace/creation_result_*.json`

---

### 更新类脚本

#### 更新用例名称
```bash
python scripts/update/update_case_names.py
```

**功能**：
- 修复用例名称缺失问题
- 从飞书数据提取完整名称
- 批量更新用例名称

---

### 同步类脚本

#### 同步用例ID到飞书
```bash
python scripts/sync/write_case_ids_to_lark.py
```

**功能**：
- 将自动化用例ID写入飞书表格
- 更新脚本序号列

#### 同步新创建的用例ID
```bash
python scripts/sync/write_new_cases_to_lark.py
```

**功能**：
- 将新创建的用例ID写入飞书表格
- 更新脚本名称和脚本序号

---

## 📋 脚本清单

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `create/create_directories_and_cases.py` | 创建目录和用例 | 飞书数据 | 创建结果JSON |
| `update/update_case_names.py` | 更新用例名称 | 飞书数据 | - |
| `sync/write_case_ids_to_lark.py` | 同步用例ID | 用例映射 | 飞书表格 |
| `sync/write_new_cases_to_lark.py` | 同步新用例ID | 创建结果 | 飞书表格 |

---

## ⚙️ 依赖说明

所有脚本依赖：
- `config.py` - 配置文件
- `skills/` - 能力模块
- `sandbox/workspace/` - 数据文件

---

## 🔧 开发新脚本

### 脚本模板

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本说明
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入依赖
from config import *
from skills.xxx import xxx

def main():
    """主函数"""
    # 1. 读取数据
    # 2. 处理逻辑
    # 3. 输出结果
    pass

if __name__ == "__main__":
    main()
```

### 命名规范

- **创建类**: `create_*.py`
- **更新类**: `update_*.py`
- **同步类**: `sync_*.py`
- **迁移类**: `migrate_*.py`

---

**维护者**: 魏斌  
**更新时间**: 2026-03-04
