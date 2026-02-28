---
name: batch-case-creator
description: 从飞书表格批量创建SDET自动化测试用例。当需要从飞书表格筛选符合条件的测试用例并批量创建到SDET平台时使用此技能。适用于需要自动化生成测试用例的场景，特别是从Excel或在线表格导入测试用例的情况。
---

# Batch Case Creator

## Overview

从飞书表格批量创建自动化测试用例到SDET平台的自动化工具。该技能自动读取飞书表格数据，筛选符合条件（是否支持自动化=是且脚本序号为空）的测试用例，并在指定目录下创建自动化用例，同时引用公共步骤。

## Core Capabilities

### 1. 飞书表格数据读取
- 自动连接飞书API读取指定表格
- 支持指定sheet_id或使用第一个sheet
- 自动解析表格数据为结构化字典列表
- 处理飞书特有的mention等复杂类型

### 2. 智能数据筛选
- 筛选条件：`是否支持自动化 == "是"` 且 `脚本序号为空或null`
- 自动过滤不符合条件的记录
- 输出筛选统计信息

### 3. 批量用例创建
- 在指定目录下创建自动化用例
- 自动复制公共步骤（从caseid=51401）
- 支持重名检测和错误处理
- 只新增不删除，确保安全

## Workflow

### Phase 1: 读取飞书表格

使用飞书API读取表格数据：

```python
# 使用scripts/read_lark_sheet.py脚本
python scripts/read_lark_sheet.py --url "https://ruijie.feishu.cn/sheets/..." --output "data.json"
```

**关键参数：**
- `url`: 飞书表格URL（包含spreadsheet_token和sheet_id）
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥
- `output`: 输出JSON文件路径（可选）

### Phase 2: 筛选符合条件的记录

筛选逻辑：
1. 检查 `是否支持自动化` 字段是否为 "是"
2. 检查 `脚本序号` 字段是否为空或null
3. 只保留同时满足两个条件的记录

**示例：**
```python
filtered_cases = [
    case for case in cases
    if case.get("是否支持自动化") == "是" and not case.get("脚本序号")
]
```

### Phase 3: 创建自动化用例

使用PlatformClient批量创建用例：

1. **初始化客户端**
```python
from platform_client import PlatformClient

client = PlatformClient(
    base_url="https://sdet.ruishan.cc/api/sdet-atp",
    token="YOUR_TOKEN",
    creator_name="自动化脚本",
    creator_id="9999"
)
```

2. **查询公共步骤**
```python
# 查询caseid=51401的步骤列表
public_steps = client.list_steps(case_id=51401)
```

3. **批量创建用例**
```python
for case_data in filtered_cases:
    # 创建用例
    result = client.create_case(
        name=case_data["用例名称"],
        directory_id=66241,  # 目标目录
        description=case_data.get("用例描述", "")
    )
    
    if result['success']:
        case_id = result['data']
        
        # 复制公共步骤
        for step in public_steps['data']:
            client.create_step(
                case_id=case_id,
                name=step['name'],
                order=step['order'],
                # 复制其他必要字段...
            )
```

### Phase 4: 执行与验证

执行批量创建脚本：

```bash
# 使用主脚本
python scripts/batch_create_cases.py \
    --sheet-url "https://ruijie.feishu.cn/sheets/..." \
    --directory-id 66241 \
    --public-case-id 51401 \
    --dry-run  # 先预览，不实际创建
```

**参数说明：**
- `--sheet-url`: 飞书表格URL
- `--directory-id`: 目标目录ID（默认66241）
- `--public-case-id`: 公共步骤用例ID（默认51401）
- `--dry-run`: 预览模式，只显示将要创建的用例，不实际创建
- `--limit`: 限制创建数量（用于测试）

## Safety Constraints

⚠️ **重要约束：**

1. **只新增不删除** - 绝对不会删除任何已有的自动化用例或目录
2. **幂等性** - 如果用例已存在（同名），跳过创建而不是报错
3. **dry-run优先** - 建议先使用`--dry-run`预览再实际执行
4. **错误隔离** - 单个用例创建失败不影响其他用例的创建
5. **日志记录** - 详细记录每个操作的执行结果

## Resources

### scripts/
- `read_lark_sheet.py` - 飞书表格读取脚本
- `batch_create_cases.py` - 批量创建用例主脚本
- `copy_public_steps.py` - 复制公共步骤工具脚本

### references/
- `api_reference.md` - SDET平台API参考文档
- `lark_api_guide.md` - 飞书API使用指南
- `field_mapping.md` - 表格字段映射说明

### assets/
- `config_template.json` - 配置文件模板

## Common Use Cases

### 用例1: 从飞书表格创建自动化用例
```bash
# 用户请求: "帮我从飞书表格创建自动化用例，放在66241目录下"
python scripts/batch_create_cases.py \
    --sheet-url "https://ruijie.feishu.cn/sheets/K8V2sTKLyhE54Ot75EycbnKLnvb?sheet=FYZ5JP" \
    --directory-id 66241
```

### 用例2: 预览将要创建的用例
```bash
# 用户请求: "先预览一下飞书表格中有哪些用例需要创建"
python scripts/batch_create_cases.py \
    --sheet-url "https://ruijie.feishu.cn/sheets/..." \
    --dry-run
```

### 用例3: 测试模式（只创建1条）
```bash
# 用户请求: "先创建1条试试效果"
python scripts/batch_create_cases.py \
    --sheet-url "https://ruijie.feishu.cn/sheets/..." \
    --directory-id 66241 \
    --limit 1
```

## Troubleshooting

### 问题1: 飞书API认证失败
**原因**: app_id或app_secret配置错误
**解决**: 检查`config.json`中的飞书应用配置

### 问题2: 创建用例失败
**可能原因**:
- Token过期或无效
- 目标目录不存在
- 用例名称重复
- 网络连接问题

**排查步骤**:
1. 使用`--dry-run`验证筛选结果
2. 检查SDET平台Token是否有效
3. 确认目标目录ID正确
4. 查看详细日志输出

### 问题3: 公共步骤复制失败
**原因**: caseid=51401不存在或无访问权限
**解决**: 确认公共步骤用例存在且有读取权限

## Dependencies

- Python 3.7+
- requests库
- PlatformClient模块（位于`../platform-client/`）

## Configuration

配置文件示例（`config.json`）：
```json
{
    "lark": {
        "app_id": "cli_a83faf50a228900e",
        "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    },
    "sdet": {
        "base_url": "https://sdet.ruishan.cc/api/sdet-atp",
        "token": "YOUR_TOKEN",
        "creator_name": "自动化脚本",
        "creator_id": "9999"
    },
    "defaults": {
        "directory_id": 66241,
        "public_case_id": 51401
    }
}
```
