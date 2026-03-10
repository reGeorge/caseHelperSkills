# Batch Case Creator

> **⚠️ 使用前必读**：调用本模块进行批量创建前，必须先完成 Phase 0 状态矩阵分析并获得用户 `Approve`。
> 详见 `.github/copilot-instructions.md` 和 `SYSTEM_PROMPT.md` 中的「强制前置执行规则」。
> 未经 Phase 0 审批直接批量调用 `create_case` / `create_step` 是被禁止的。

## Overview

从飞书表格批量创建测试用例到SDET平台的自动化工具。该技能支持：
- 从JSON文件或飞书表格读取测试用例数据
- 按关键词筛选符合条件的用例
- 在指定目录下创建用例（支持个人用例和自动化用例）
- 将创建的Case ID回写到飞书表格

## Core Capabilities

### 1. 数据源读取
- **飞书表格读取**: 自动连接飞书API读取指定表格
- **JSON文件读取**: 从本地JSON文件读取用例数据
- 支持指定sheet_id或使用第一个sheet
- 自动解析为结构化字典列表

### 2. 智能数据筛选
- **关键词筛选**: 按用例名称/描述中的关键词筛选
- **条件筛选**: 支持自定义筛选条件
- 自动过滤不符合条件的记录
- 输出筛选统计信息

### 3. 批量用例创建
- **用例类型支持**: 支持个人用例(type=1)和自动化用例(默认)
- 在指定目录下批量创建用例
- 支持重名检测和错误处理
- 只新增不删除，确保安全

### 4. 飞书回写
- 将创建的Case ID写入飞书表格指定列
- 支持指定sheet_id和列名
- 基于行号映射关系准确回写

## Workflow

### Phase 1: 读取数据源

**方案A: 从飞书表格读取**
```python
# 使用scripts/read_lark_sheet.py脚本
python scripts/read_lark_sheet.py --url "https://ruijie.feishu.cn/sheets/..." --output "data.json"
```

**方案B: 从JSON文件读取**
```python
import json
with open('test_cases.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)
```

### Phase 2: 筛选符合条件的记录

**关键词筛选**（按用例名称/描述）：
```python
keywords = ["用户进行有线认证", "有线portal认证", "有线1x认证"]

def match_keywords(case):
    text = case.get("用例名称", "") + " " + case.get("用例描述", "")
    return any(kw in text for kw in keywords)

filtered_cases = [case for case in cases if match_keywords(case)]
```

**条件筛选**：
```python
filtered_cases = [
    case for case in cases
    if case.get("是否支持自动化") == "是" and not case.get("脚本序号")
]
```

### Phase 3: 创建测试用例

使用PlatformClient批量创建用例：

1. **初始化客户端**
```python
from platform_client import PlatformClient
import os

client = PlatformClient(
    base_url=os.getenv('SDET_BASE_URL'),
    token=os.getenv('SDET_API_TOKEN'),
    creator_name="自动化脚本",
    creator_id="9999"
)
```

2. **批量创建用例**
```python
results = []
for idx, case_data in enumerate(filtered_cases):
    result = client.create_case(
        name=case_data["用例名称"],
        directory_id=66346,  # 目标目录
        description=case_data.get("用例描述", ""),
        priority=2,
        type=1  # 个人用例
    )

    if result['success']:
        case_id = result['data']
        results.append({
            "row_number": idx + 1,
            "case_name": case_data["用例名称"],
            "case_id": case_id,
            "success": True
        })
    else:
        results.append({
            "row_number": idx + 1,
            "case_name": case_data["用例名称"],
            "success": False,
            "message": result.get('message', '创建失败')
        })
```

3. **保存创建结果**
```python
import json

summary = {
    "total": len(filtered_cases),
    "success_count": sum(1 for r in results if r["success"]),
    "failed_count": sum(1 for r in results if not r["success"]),
    "results": results
}

with open('create_result.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
```

### Phase 4: 回写飞书表格

将创建的Case ID写入飞书表格：

```python
import requests

# 获取飞书access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/'
token_resp = requests.post(token_url, json={
    'app_id': os.getenv('LARK_APP_ID'),
    'app_secret': os.getenv('LARK_APP_SECRET')
})
access_token = token_resp.json()['app_access_token']

# 写入Case ID
spreadsheet_token = "Mw7escaVhh92SSts8incmbbUnkc"
sheet_id = "dfa872"
column_letter = "R"  # 脚本序号列

for result in results:
    if result['success']:
        excel_row = result['row_number'] + 2  # 加表头行数
        case_id = result['case_id']

        range_str = f'{sheet_id}!{column_letter}{excel_row}:{column_letter}{excel_row}'
        data = {
            'valueRange': {
                'range': range_str,
                'values': [[str(case_id)]]
            }
        }

        write_url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
        resp = requests.put(write_url, headers={'Authorization': f'Bearer {access_token}'}, json=data)

        if resp.json().get('code') == 0:
            print(f'行{excel_row}: Case ID {case_id} 写入成功')
        else:
            print(f'行{excel_row}: 写入失败 - {resp.json()}')
```

### Phase 5: 执行与验证

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

### 用例1: 按关键词筛选并创建个人用例
```python
# 筛选"用户进行有线认证"相关用例，创建为个人用例(type=1)
keywords = ["用户进行有线认证", "有线portal认证", "有线1x认证"]
filtered_cases = [
    case for case in cases
    if any(kw in case.get("用例名称", "") for kw in keywords)
]

# 创建到66346目录
for case in filtered_cases:
    client.create_case(
        name=case["用例名称"],
        directory_id=66346,
        type=1  # 个人用例
    )
```

### 用例2: 从飞书表格读取并创建
```bash
# 读取飞书表格
python scripts/read_lark_sheet.py \
    --url "https://ruijie.feishu.cn/sheets/...?sheet=xxx" \
    --output "data.json"

# 创建用例
python scripts/batch_create_cases.py \
    --input "data.json" \
    --directory-id 66346 \
    --type 1
```

### 用例3: 回写Case ID到飞书
```bash
# 使用创建结果回写
python scripts/write_case_ids.py \
    --create-result "create_result.json" \
    --spreadsheet-token "Mw7escaVhh92SSts8incmbbUnkc" \
    --sheet-id "dfa872" \
    --column "R"
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
1. 检查SDET平台Token是否有效
2. 确认目标目录ID正确
3. 查看详细日志输出
4. 检查`create_result.json`中的失败原因

### 问题3: 飞书回写失败（91403 Forbidden）
**可能原因**:
- 飞书应用无表格编辑权限
- spreadsheet_token或sheet_id错误

**解决方案**:
1. 在飞书开放平台开通`sheets:spreadsheet`权限
2. 将应用服务账号添加为表格协作者
3. 确认spreadsheet_token从完整URL中正确提取
4. 确认sheet_id与URL中的参数一致

**正确URL格式**:
```
https://ruijie.feishu.cn/sheets/{spreadsheet_token}?sheet={sheet_id}
```

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
