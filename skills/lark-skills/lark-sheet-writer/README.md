# 飞书表格记录写入器

这个skill用于写入和编辑飞书表格的记录，支持指定工作表、批量操作等功能。

## 功能特点

- ✅ 写入新记录到指定工作表
- ✅ 编辑现有记录
- ✅ 批量写入和更新记录
- ✅ 支持从JSON文件导入数据
- ✅ 自动处理表头和数据映射
- ✅ 支持指定单元格范围操作
- ✅ 支持命令行和Python API两种使用方式

## 支持的操作

### 1. 写入操作
- ✅ 写入单条记录
- ✅ 批量写入多条记录
- ✅ 从JSON文件导入数据

### 2. 编辑操作
- ✅ 基于条件更新记录
- ✅ 批量更新符合条件的记录

### 3. 高级功能
- ✅ 数据验证
- ✅ 单元格范围操作
- ✅ 错误处理

## 文件说明

- `SKILL.md`: Skill详细说明文档
- `lark_sheet_writer.py`: 核心写入器实现
- `example_usage.py`: 使用示例代码
- `README.md`: 本文件

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 命令行使用

#### 写入单条记录

```bash
python lark_sheet_writer.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --spreadsheet-token "OXndwZNS9i6hhjk16VwcRai5ngd" \
  --sheet-id "9LD59B" \
  --action "write" \
  --record '{"用例名称": "测试用例1", "用例描述": "测试功能", "预置条件": "无", "测试步骤": "1. 步骤1\n2. 步骤2", "期望结果": "测试通过", "是否支持自动化": "是"}'
```

#### 批量写入记录

```bash
python lark_sheet_writer.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --spreadsheet-token "OXndwZNS9i6hhjk16VwcRai5ngd" \
  --sheet-id "9LD59B" \
  --action "write" \
  --records '[{"用例名称": "测试用例2", "用例描述": "测试功能2", "预置条件": "无", "测试步骤": "1. 步骤1\n2. 步骤2", "期望结果": "测试通过", "是否支持自动化": "是"}, {"用例名称": "测试用例3", "用例描述": "测试功能3", "预置条件": "无", "测试步骤": "1. 步骤1\n2. 步骤2", "期望结果": "测试通过", "是否支持自动化": "否"}]'
```

#### 更新记录

```bash
python lark_sheet_writer.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --spreadsheet-token "OXndwZNS9i6hhjk16VwcRai5ngd" \
  --sheet-id "9LD59B" \
  --action "update" \
  --condition '{"用例名称": "测试用例1"}' \
  --update-data '{"用例描述": "更新的测试描述", "是否支持自动化": "否"}'
```

#### 从JSON文件导入

```bash
python lark_sheet_writer.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --spreadsheet-token "OXndwZNS9i6hhjk16VwcRai5ngd" \
  --sheet-id "9LD59B" \
  --action "import" \
  --json-file "test_cases.json"
```

### 3. Python API使用

```python
from lark_sheet_writer import LarkSheetWriter

# 配置
app_id = "cli_a83faf50a228900e"
app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

# 创建写入器
writer = LarkSheetWriter(app_id, app_secret)

# 表格信息
spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"
sheet_id = "9LD59B"

# 写入单条记录
record = {
    "用例名称": "测试用例1",
    "用例描述": "测试功能",
    "预置条件": "无",
    "测试步骤": "1. 步骤1\n2. 步骤2",
    "期望结果": "测试通过",
    "是否支持自动化": "是"
}

result = writer.write_record(spreadsheet_token, sheet_id, record)
print(result)

# 更新记录
condition = {"用例名称": "测试用例1"}
update_data = {"用例描述": "更新的描述"}

result = writer.update_record(spreadsheet_token, sheet_id, condition, update_data)
print(result)
```

## 使用示例

查看 `example_usage.py` 文件获取更多使用示例：

1. **写入单条记录**
2. **批量写入多条记录**
3. **更新现有记录**
4. **从JSON文件导入数据**
5. **验证数据格式**
6. **批量操作演示**

运行示例：

```bash
python example_usage.py
```

## 数据格式

### 输入格式

#### 单条记录

```python
{
    "用例名称": "测试用例1",
    "用例描述": "测试功能1",
    "预置条件": "无",
    "测试步骤": "1. 步骤1\n2. 步骤2",
    "期望结果": "测试通过",
    "是否支持自动化": "是"
}
```

#### 多条记录

```python
[
    {
        "用例名称": "测试用例1",
        "用例描述": "测试功能1",
        "预置条件": "无",
        "测试步骤": "1. 步骤1\n2. 步骤2",
        "期望结果": "测试通过",
        "是否支持自动化": "是"
    },
    {
        "用例名称": "测试用例2",
        "用例描述": "测试功能2",
        "预置条件": "无",
        "测试步骤": "1. 步骤1\n2. 步骤2",
        "期望结果": "测试通过",
        "是否支持自动化": "否"
    }
]
```

### 输出格式

#### 成功响应

```json
{
  "success": true,
  "message": "写入成功",
  "data": {
    "updated_rows": 1,
    "inserted_rows": 1
  }
}
```

#### 失败响应

```json
{
  "success": false,
  "message": "写入失败",
  "error": "错误信息"
}
```

## 参数说明

### 命令行参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--app-id` | 是 | 飞书应用ID |
| `--app-secret` | 是 | 飞书应用密钥 |
| `--spreadsheet-token` | 是 | 表格token |
| `--sheet-id` | 是 | 工作表ID |
| `--action` | 是 | 操作类型（write/update/import） |
| `--record` | 否 | 单条记录数据（JSON格式） |
| `--records` | 否 | 多条记录数据（JSON格式） |
| `--condition` | 否 | 更新条件（JSON格式） |
| `--update-data` | 否 | 更新数据（JSON格式） |
| `--json-file` | 否 | JSON文件路径 |
| `--clear-existing` | 否 | 是否清空现有数据 |

### Python API参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `app_id` | str | 是 | 飞书应用ID |
| `app_secret` | str | 是 | 飞书应用密钥 |
| `spreadsheet_token` | str | 是 | 表格token |
| `sheet_id` | str | 是 | 工作表ID |
| `record` | dict | 否 | 单条记录数据 |
| `records` | list | 否 | 多条记录数据 |
| `condition` | dict | 否 | 更新条件 |
| `update_data` | dict | 否 | 更新数据 |
| `json_file` | str | 否 | JSON文件路径 |
| `clear_existing` | bool | 否 | 是否清空现有数据 |

## 权限要求

确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readwrite`: 读写权限

## 常见问题

### 1. 如何获取工作表ID？

使用 `lark-sheets` skill 获取工作表列表：

```bash
cd ../lark-sheets
python lark_sheets.py
```

### 2. 如何处理表头不匹配的情况？

- 确保数据字段名与表头完全一致
- 缺失的字段会被自动填充为空值
- 多余的字段会被忽略

### 3. 如何批量更新多条记录？

使用 `update_record` 方法，设置条件来匹配多条记录：

```python
condition = {"是否支持自动化": "是"}
update_data = {"期望结果": "自动化测试通过"}
result = writer.update_record(spreadsheet_token, sheet_id, condition, update_data)
```

### 4. 如何验证数据格式？

使用 `validate_data` 方法验证数据：

```python
required_fields = ["用例名称", "测试步骤", "期望结果"]
result = writer.validate_data(records, required_fields)
```

## 高级用法

### 1. 数据验证

```python
# 验证必填字段
required_fields = ["用例名称", "测试步骤", "期望结果"]
validation_result = writer.validate_data(records, required_fields)

if not validation_result["valid"]:
    print(f"数据验证失败: {validation_result['errors']}")
```

### 2. 批量导入

```python
# 从JSON文件导入并清空现有数据
result = writer.import_from_json(
    spreadsheet_token, sheet_id, "test_cases.json", clear_existing=True
)
```

### 3. 条件更新

```python
# 多条件更新
condition = {
    "用例名称": "测试用例",
    "是否支持自动化": "是"
}
update_data = {"期望结果": "测试通过"}
result = writer.update_record(spreadsheet_token, sheet_id, condition, update_data)
```

## 注意事项

- 确保access_token有效且未过期
- 确保应用有表格写入权限
- 表头必须与数据字段名匹配
- 批量操作时注意API调用限制
- 建议先在测试环境中验证操作
- 空值会被自动处理为空字符串
- 支持中文字段名

## 相关Skills

- `lark-access-token`: 获取飞书API的access_token
- `lark-sheets`: 获取飞书表格的工作表列表
- `lark-sheet-reader`: 读取飞书表格内容
- `lark-api-helper`: 飞书API综合助手

## 更新日志

### v1.0.0 (2026-02-28)
- ✅ 初始版本发布
- ✅ 支持写入单条记录
- ✅ 支持批量写入多条记录
- ✅ 支持基于条件更新记录
- ✅ 支持从JSON文件导入数据
- ✅ 支持命令行和Python API
- ✅ 支持数据验证
