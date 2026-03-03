# 飞书表格写入问题记录与解决方案

## 问题1: Range格式错误

### 错误现象
使用错误的range格式导致写入失败

### 错误格式
```
sheet_id!A1  # 缺少结束单元格
```

### 正确格式
```
sheet_id!A1:A1  # 起始和结束单元格相同
```

### 示例
```python
# 写入单个单元格（第18列第9行）
range_str = f"{sheet_id}!R9:R9"

# 写入范围（第18列第9-15行）
range_str = f"{sheet_id}!R9:R15"
```

## 问题2: Windows控制台编码问题

### 错误现象
```
UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'
```

### 原因
Windows PowerShell默认使用GBK编码，无法显示Unicode特殊字符（如✓、❌等）

### 解决方案
1. 使用ASCII字符替代特殊符号
2. 或在脚本开头设置UTF-8编码：
```python
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

## 问题3: 列号转字母

### 需求
将列号（1, 2, 3...）转换为Excel列字母（A, B, C...Z, AA, AB...）

### 解决方案
```python
def col_number_to_letter(col_num):
    """将列号转换为字母"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(65 + col_num % 26) + result
        col_num //= 26
    return result

# 示例
col_number_to_letter(1)   # 'A'
col_number_to_letter(18)  # 'R'
col_number_to_letter(27)  # 'AA'
```

## 最佳实践

### 1. 测试先行
先测试一条记录，确认成功后再批量执行：
```python
TEST_MODE = True  # 测试模式
TEST_MODE = False  # 批量模式
```

### 2. 错误处理
记录详细的错误信息：
```python
try:
    result = write_to_cell(...)
    if not result.get('success'):
        errors.append({
            'row': row_idx,
            'error': result.get('message'),
            'code': result.get('code')
        })
except Exception as e:
    # 记录异常
    with open('error.log', 'w') as f:
        f.write(traceback.format_exc())
```

### 3. 日志输出
输出详细的执行日志：
```python
print(f"请求URL: {url}")
print(f"Range: {range_str}")
print(f"Value: {value}")
print(f"响应: code={result.get('code')}, msg={result.get('msg')}")
```

## API调用示例

### 写入单个单元格
```python
url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
payload = {
    "valueRange": {
        "range": "dfa872!R9:R9",
        "values": [["66396"]]
    }
}
response = requests.put(url, headers=headers, json=payload)
```

### 读取表格数据
```python
url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers)
data = response.json().get("data", {}).get("valueRange", {}).get("values", [])
```

## 参考链接
- 飞书开放平台: https://open.feishu.cn/document/server-docs/docs/sheets-v3/
- 表格API文档: https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-overview
