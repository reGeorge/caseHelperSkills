# 飞书表格内容读取器

这个skill用于读取飞书表格的内容，并将其转换为JSON格式输出。

## 功能特点

- ✅ 读取指定飞书表格链接的内容
- ✅ 支持读取测试用例表格
- ✅ 自动识别表头作为JSON的key
- ✅ 输出标准JSON格式数据
- ✅ 支持多工作表读取
- ✅ 支持从URL直接读取
- ✅ 支持命令行和Python API两种使用方式

## 支持的测试用例格式

本skill专门支持测试用例表格，包含以下列：
- 用例名称
- 用例描述
- 预置条件
- 测试步骤
- 期望结果
- 是否支持自动化

## 文件说明

- `SKILL.md`: Skill详细说明文档
- `lark_sheet_reader.py`: 核心读取器实现
- `example_usage.py`: 使用示例代码
- `README.md`: 本文件

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 命令行使用

#### 从URL读取

```bash
python lark_sheet_reader.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --url "https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI"
```

#### 读取指定工作表

```bash
python lark_sheet_reader.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --spreadsheet-token "OXndwZNS9i6hhjk16VwcRai5ngd" \
  --sheet-id "9LD59B"
```

#### 保存到文件

```bash
python lark_sheet_reader.py \
  --app-id "cli_a83faf50a228900e" \
  --app-secret "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH" \
  --url "https://ruijie.feishu.cn/sheets/xxx" \
  --output "test_cases.json"
```

### 3. Python API使用

```python
from lark_sheet_reader import LarkSheetReader

# 配置
app_id = "cli_a83faf50a228900e"
app_secret = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

# 创建读取器
reader = LarkSheetReader(app_id, app_secret)

# 从URL读取
url = "https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI"
data = reader.read_from_url(url)

# 输出JSON
print(reader.to_json(data))

# 保存到文件
reader.save_to_file(data, "test_cases.json")
```

## 使用示例

查看 `example_usage.py` 文件获取更多使用示例：

1. **从URL读取表格内容**
2. **读取指定工作表**
3. **读取第一个工作表**
4. **过滤数据**
5. **批量读取多个工作表**

运行示例：

```bash
python example_usage.py
```

## 输出格式

### JSON输出示例

```json
[
  {
    "用例名称": "登录功能测试",
    "用例描述": "验证用户登录功能",
    "预置条件": "用户已注册",
    "测试步骤": "1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮",
    "期望结果": "登录成功，跳转到首页",
    "是否支持自动化": "是"
  },
  {
    "用例名称": "注册功能测试",
    "用例描述": "验证用户注册功能",
    "预置条件": "无",
    "测试步骤": "1. 打开注册页面\n2. 填写注册信息\n3. 点击注册按钮",
    "期望结果": "注册成功，跳转到登录页面",
    "是否支持自动化": "是"
  }
]
```

## 参数说明

### 命令行参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--app-id` | 是 | 飞书应用ID |
| `--app-secret` | 是 | 飞书应用密钥 |
| `--url` | 否 | 飞书表格URL（与--spreadsheet-token二选一） |
| `--spreadsheet-token` | 否 | 表格token（与--url二选一） |
| `--sheet-id` | 否 | 工作表ID（不指定则读取第一个工作表） |
| `--output` | 否 | 输出文件名 |

### Python API参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `app_id` | str | 是 | 飞书应用ID |
| `app_secret` | str | 是 | 飞书应用密钥 |
| `spreadsheet_token` | str | 是 | 表格token |
| `sheet_id` | str | 否 | 工作表ID |
| `url` | str | 否 | 飞书表格URL |

## 权限要求

确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readonly`: 只读权限

## 常见问题

### 1. 如何获取表格token？

表格token可以从飞书表格URL中获取：
```
https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
                                  这部分就是spreadsheet_token
```

### 2. 如何获取工作表ID？

使用 `lark-sheets` skill 获取工作表列表：

```bash
cd ../lark-sheets
python lark_sheets.py
```

### 3. 如何处理空值？

空单元格会被自动设置为 `null`，在JSON中表示为 `None`。

### 4. 支持中文表头吗？

支持！表头会直接作为JSON的key，包括中文字段名。

## 高级用法

### 数据过滤

```python
# 只读取支持自动化的用例
auto_cases = [
    case for case in data 
    if case.get("是否支持自动化") == "是"
]
```

### 批量读取

```python
# 读取多个工作表
sheet_ids = ["9LD59B", "KFphLl", "9395c9"]
all_data = {}

for sheet_id in sheet_ids:
    data = reader.read_sheet(spreadsheet_token, sheet_id)
    all_data[sheet_id] = data
```

### 数据验证

```python
# 验证必填字段
required_columns = ["用例名称", "测试步骤", "期望结果"]

for case in data:
    for column in required_columns:
        if not case.get(column):
            print(f"警告: 用例 '{case.get('用例名称')}' 缺少字段 '{column}'")
```

## 注意事项

- access_token有有效期，通常为2小时
- 请妥善保管app_secret和access_token
- 表格第一行应为表头
- 空单元格将被设置为null
- 支持中文字段名作为key

## 相关Skills

- `lark-access-token`: 获取飞书API的access_token
- `lark-sheets`: 获取飞书表格的工作表列表
- `lark-api-helper`: 飞书API综合助手

## 更新日志

### v1.0.0 (2026-02-28)
- ✅ 初始版本发布
- ✅ 支持从URL读取表格内容
- ✅ 支持读取指定工作表
- ✅ 支持JSON格式输出
- ✅ 支持命令行和Python API
