# 飞书表格记录写入器

这个skill帮助用户写入和编辑飞书表格的记录，支持指定工作表、批量操作等功能。

## 功能说明

- 写入新记录到指定工作表
- 编辑现有记录
- 批量写入和更新记录
- 支持从JSON文件导入数据
- 自动处理表头和数据映射
- 支持指定单元格范围操作

## 使用场景

当用户需要：
- 向飞书表格添加新的测试用例
- 更新表格中的现有记录
- 批量导入数据到表格
- 自动化表格数据维护
- 同步外部数据到飞书表格

## 支持的操作

### 1. 写入新记录
- 追加新记录到表格末尾
- 插入记录到指定位置
- 批量添加多条记录

### 2. 编辑现有记录
- 更新指定行的记录
- 基于条件更新记录
- 批量更新多条记录

### 3. 单元格级写入（推荐用于Case ID回写）
- 写入单个单元格
- 基于Range格式写入
- 支持批量单元格写入

### 4. 批量操作
- 从JSON文件批量导入数据
- 批量更新符合条件的记录
- 批量删除记录

## 使用方法

### 1. 基本使用

```python
from lark_sheet_writer import LarkSheetWriter

# 初始化写入器
writer = LarkSheetWriter(
    app_id="your_app_id",
    app_secret="your_app_secret",
    spreadsheet_token="your_spreadsheet_token"
)

# 写入新记录
record = {
    "用例名称": "测试用例1",
    "用例描述": "测试功能",
    "预置条件": "无",
    "测试步骤": "1. 步骤1\n2. 步骤2",
    "期望结果": "测试通过",
    "是否支持自动化": "是"
}

# 写入到指定工作表
result = writer.write_record(sheet_id="your_sheet_id", record=record)
print(f"写入结果: {result}")

# 编辑现有记录
update_data = {
    "用例描述": "更新的测试描述",
    "是否支持自动化": "否"
}

# 基于条件更新
result = writer.update_record(
    sheet_id="your_sheet_id",
    condition={"用例名称": "测试用例1"},
    update_data=update_data
)
print(f"更新结果: {result}")
```

### 2. 批量操作

```python
# 批量写入多条记录
records = [
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

# 批量写入
result = writer.write_records(sheet_id="your_sheet_id", records=records)
print(f"批量写入结果: {result}")

# 从JSON文件导入
result = writer.import_from_json(
    sheet_id="your_sheet_id",
    json_file="test_cases.json"
)
print(f"导入结果: {result}")
```

### 3. 单元格级写入（推荐用于Case ID回写）

```python
import requests
import os

# 获取access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/'
token_resp = requests.post(token_url, json={
    'app_id': os.getenv('LARK_APP_ID'),
    'app_secret': os.getenv('LARK_APP_SECRET')
})
access_token = token_resp.json()['app_access_token']

# 写入单个单元格
spreadsheet_token = "Mw7escaVhh92SSts8incmbbUnkc"
sheet_id = "dfa872"

# Range格式: sheet_id!列字母行号:列字母行号
range_str = f'{sheet_id}!R6:R6'  # 写入R列第6行

write_url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

data = {
    'valueRange': {
        'range': range_str,
        'values': [['66330']]  # 二维数组格式
    }
}

resp = requests.put(write_url, headers=headers, json=data)
if resp.json().get('code') == 0:
    print('写入成功')
else:
    print(f'写入失败: {resp.json()}')
```

**关键点**:
- Range格式必须是 `sheet_id!列字母行号:列字母行号`，例如 `dfa872!R6:R6`
- values必须是二维数组 `[[值]]`，不能是单值
- 行号从1开始，第1行通常是表头
- Excel行号 = 数据索引 + 2（表头行）

**批量写入示例**:
```python
case_id_mapping = {
    6: 66330,
    8: 66331,
    15: 66332
}

for excel_row, case_id in case_id_mapping.items():
    range_str = f'{sheet_id}!R{excel_row}:R{excel_row}'
    data = {'valueRange': {'range': range_str, 'values': [[str(case_id)]]}}
    resp = requests.put(write_url, headers=headers, json=data)
    # 处理响应...
```

### 4. 命令行使用

```bash
# 写入单条记录
python lark_sheet_writer.py \
  --app-id "your_app_id" \
  --app-secret "your_app_secret" \
  --spreadsheet-token "your_spreadsheet_token" \
  --sheet-id "your_sheet_id" \
  --action "write" \
  --record '{"用例名称": "测试用例", "用例描述": "测试功能"}'

# 更新记录
python lark_sheet_writer.py \
  --app-id "your_app_id" \
  --app-secret "your_app_secret" \
  --spreadsheet-token "your_spreadsheet_token" \
  --sheet-id "your_sheet_id" \
  --action "update" \
  --condition '{"用例名称": "测试用例"}' \
  --update-data '{"用例描述": "更新的描述"}'

# 从JSON文件导入
python lark_sheet_writer.py \
  --app-id "your_app_id" \
  --app-secret "your_app_secret" \
  --spreadsheet-token "your_spreadsheet_token" \
  --sheet-id "your_sheet_id" \
  --action "import" \
  --json-file "test_cases.json"
```

## 参数说明

### 必需参数
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥
- `spreadsheet_token`: 表格token
- `sheet_id`: 工作表ID

### 操作参数

#### 写入操作
- `record`: 单条记录数据（字典）
- `records`: 多条记录数据（列表）
- `insert_position`: 插入位置（可选）

#### 更新操作
- `condition`: 更新条件（字典）
- `update_data`: 更新数据（字典）
- `row_index`: 行索引（可选）

#### 导入操作
- `json_file`: JSON文件路径
- `clear_existing`: 是否清空现有数据（布尔值）

## API端点

### 写入单元格数据
```
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
```

### 批量写入数据
```
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update
```

## 数据格式

### 输入格式

#### 单条记录
```python
{
    "用例名称": "测试用例",
    "用例描述": "测试功能",
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
```python
{
    "success": True,
    "message": "操作成功",
    "data": {
        "updated_rows": 1,
        "inserted_rows": 0
    }
}
```

#### 失败响应
```python
{
    "success": False,
    "message": "操作失败",
    "error": "错误信息"
}
```

## 数据处理流程

1. **获取Access Token**
   - 使用app_id和app_secret获取token
   - 自动处理token有效期

2. **读取表头**
   - 读取工作表的表头信息
   - 建立字段映射关系

3. **数据转换**
   - 将字典格式转换为表格行数据
   - 处理空值和特殊字符

4. **执行操作**
   - 写入新记录
   - 编辑现有记录
   - 批量操作

5. **返回结果**
   - 返回操作结果
   - 处理错误信息

## 配置要求

### 依赖库
```bash
pip install requests
```

### 权限要求
确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readwrite`: 读写权限

## 高级功能

### 1. 条件更新
```python
# 基于条件更新
result = writer.update_record(
    sheet_id="your_sheet_id",
    condition={
        "用例名称": "测试用例",
        "是否支持自动化": "是"
    },
    update_data={"期望结果": "测试通过"}
)
```

### 2. 批量导入
```python
# 从JSON文件批量导入
result = writer.import_from_json(
    sheet_id="your_sheet_id",
    json_file="test_cases.json",
    clear_existing=True  # 清空现有数据
)
```

### 3. 数据验证
```python
# 验证数据格式
result = writer.validate_data(
    records=records,
    required_fields=["用例名称", "测试步骤", "期望结果"]
)

if not result["valid"]:
    print(f"数据验证失败: {result['errors']}")
```

### 4. 单元格范围操作
```python
# 写入指定范围
result = writer.write_range(
    sheet_id="your_sheet_id",
    range="A2:E5",
    values=[
        ["测试用例1", "测试功能1", "无", "步骤1", "通过"],
        ["测试用例2", "测试功能2", "无", "步骤2", "通过"]
    ]
)
```

## 最佳实践

1. **数据验证**
   - 写入前验证数据格式
   - 检查必填字段

2. **错误处理**
   - 捕获并处理API异常
   - 记录操作日志

3. **性能优化**
   - 批量操作减少API调用
   - 合理使用缓存

4. **安全性**
   - 不硬编码敏感信息
   - 使用环境变量存储凭证

5. **可靠性**
   - 实现重试机制
   - 处理网络异常

## 故障排除

### 常见问题

1. **权限不足**
   - 检查应用权限设置
   - 确保开通了sheets:spreadsheet.readwrite权限

2. **表头不匹配**
   - 检查表头名称是否正确
   - 确保字段名与表头一致

3. **数据格式错误**
   - 检查数据类型是否正确
   - 确保日期格式符合要求

4. **API调用频率限制**
   - 减少API调用频率
   - 实现批量操作

5. **网络连接问题**
   - 检查网络连接
   - 实现重试机制

6. **单元格写入失败（90215 sheetId not found）**
   - 检查sheet_id是否与URL中的参数一致
   - 确认表格URL格式正确: `https://ruijie.feishu.cn/sheets/{token}?sheet={sheet_id}`

7. **单元格写入失败（91403 Forbidden）**
   - 检查飞书应用是否有表格编辑权限
   - 在飞书开放平台开通 `sheets:spreadsheet` 权限
   - 确保应用服务账号是表格的协作者

## 注意事项

- 确保access_token有效且未过期
- 确保应用有表格写入权限
- 表头必须与数据字段名匹配
- 批量操作时注意API调用限制
- 建议先在测试环境中验证操作

## 相关Skills

- `lark-access-token`: 获取飞书API的access_token
- `lark-sheets`: 获取飞书表格的工作表列表
- `lark-sheet-reader`: 读取飞书表格内容
- `lark-api-helper`: 飞书API综合助手
