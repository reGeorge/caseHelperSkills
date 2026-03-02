# 飞书表格内容读取器

这个skill帮助用户读取飞书表格的内容，并将其转换为JSON格式输出。

## 功能说明

- 读取指定飞书表格链接的内容
- 支持读取测试用例表格
- 自动识别表头作为JSON的key
- 输出标准JSON格式数据
- 支持多工作表读取

## 使用场景

当用户需要：
- 读取飞书表格中的测试用例
- 将表格数据导出为JSON格式
- 批量获取测试用例信息
- 自动化测试用例管理

## 支持的列格式

本skill专门支持测试用例表格，包含以下列：
- 用例名称
- 用例描述
- 预置条件
- 测试步骤
- 期望结果
- 是否支持自动化

## 使用方法

### 1. 基本使用

```python
from lark_sheet_reader import LarkSheetReader

# 初始化读取器
reader = LarkSheetReader(
    app_id="your_app_id",
    app_secret="your_app_secret",
    spreadsheet_token="your_spreadsheet_token"
)

# 读取指定工作表
data = reader.read_sheet(sheet_id="your_sheet_id")

# 输出JSON
print(data.to_json())
```

### 2. 从URL读取

```python
# 从飞书表格URL直接读取
url = "https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI"
data = reader.read_from_url(url)
```

### 3. 批量读取

```python
# 读取所有工作表
all_sheets = reader.read_all_sheets()
```

## 参数说明

### 必需参数
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥
- `spreadsheet_token`: 表格token（可从URL获取）

### 可选参数
- `sheet_id`: 工作表ID（不指定则读取第一个工作表）
- `access_token`: 访问令牌（可自动获取）

## API端点

### 读取单元格数据
```
GET https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}
```

### 读取范围数据
```
GET https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
```

## 返回格式

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

## 数据处理流程

1. **获取Access Token**
   - 使用app_id和app_secret获取token
   - 自动处理token有效期

2. **读取表格数据**
   - 根据spreadsheet_token和sheet_id读取数据
   - 自动识别表头行

3. **转换为JSON**
   - 使用表头作为JSON的key
   - 每行数据作为一个JSON对象
   - 处理空值和特殊字符

4. **输出结果**
   - 返回JSON格式数据
   - 支持保存到文件

## 配置要求

### 依赖库
```bash
pip install requests
```

### 权限要求
确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readonly`: 只读权限

## 使用示例

### 命令行使用

```bash
# 读取指定表格
python lark_sheet_reader.py --url "https://ruijie.feishu.cn/sheets/xxx"

# 读取指定工作表
python lark_sheet_reader.py --spreadsheet-token "xxx" --sheet-id "xxx"

# 保存到文件
python lark_sheet_reader.py --url "xxx" --output "test_cases.json"
```

### Python脚本使用

```python
import json
from lark_sheet_reader import LarkSheetReader

# 配置
config = {
    "app_id": "cli_a83faf50a228900e",
    "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
}

# 读取表格
reader = LarkSheetReader(**config)
test_cases = reader.read_from_url(
    "https://ruijie.feishu.cn/sheets/HxOTs5bwZhz5K4tLHIdcFxY3nSb?sheet=0RTcwI"
)

# 输出JSON
print(json.dumps(test_cases, ensure_ascii=False, indent=2))

# 保存到文件
with open('test_cases.json', 'w', encoding='utf-8') as f:
    json.dump(test_cases, f, ensure_ascii=False, indent=2)
```

## 注意事项

- 确保access_token有效且未过期
- 确保应用有表格访问权限
- 表格第一行应为表头
- 空单元格将被设置为null
- 支持中文字段名作为key

## 错误处理

### 常见错误

1. **表格不存在**
   - 检查spreadsheet_token是否正确
   - 确认表格未被删除

2. **权限不足**
   - 检查应用权限设置
   - 确认表格已分享给应用

3. **工作表不存在**
   - 检查sheet_id是否正确
   - 使用lark-sheets skill获取工作表列表

4. **数据格式错误**
   - 检查表格第一行是否为表头
   - 确认数据格式符合要求

## 高级功能

### 1. 数据过滤
```python
# 只读取支持自动化的用例
auto_cases = reader.read_sheet(
    sheet_id="xxx",
    filter_column="是否支持自动化",
    filter_value="是"
)
```

### 2. 数据验证
```python
# 验证必填字段
reader.validate_data(
    required_columns=["用例名称", "测试步骤", "期望结果"]
)
```

### 3. 批量导出
```python
# 导出所有工作表
reader.export_all_sheets(output_dir="./test_cases")
```

## 最佳实践

1. **Token管理**
   - 使用lark-access-token skill获取token
   - 缓存token避免频繁请求

2. **错误处理**
   - 捕获并处理API异常
   - 记录错误日志

3. **性能优化**
   - 使用范围读取减少数据量
   - 批量处理多个工作表

4. **数据质量**
   - 验证表头完整性
   - 检查必填字段
   - 处理空值和异常数据
