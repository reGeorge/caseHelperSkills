# 飞书表格操作常见问题与解决方案

## 🔍 问题分类

### 一、Range格式问题

#### 问题1.1: Range格式错误导致写入失败

**错误现象**:
```python
# 错误的range格式
range_str = "sheet_id!A1"  # 缺少结束单元格
```

**原因分析**:
飞书API要求range格式必须包含起始和结束单元格。

**解决方案**:
```python
# 正确的range格式
range_str = "sheet_id!A1:A1"  # 单个单元格
range_str = "sheet_id!A1:B2"  # 范围
```

**完整示例**:
```python
# 写入单个单元格（第18列第9行）
range_str = f"{sheet_id}!R9:R9"
write_to_range(spreadsheet_token, range_str, [["value"]], access_token)
```

---

### 二、编码问题

#### 问题2.1: Windows控制台UnicodeEncodeError

**错误现象**:
```
UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'
```

**原因分析**:
Windows PowerShell默认使用GBK编码，无法显示Unicode特殊字符。

**解决方案**:

**方案1**: 使用ASCII字符替代
```python
# 避免
print('✓ 测试成功')

# 改用
print('[OK] 测试成功')
```

**方案2**: 设置UTF-8编码
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

### 三、列号转换问题

#### 问题3.1: 如何将列号转换为字母？

**需求**: 将数字列号（1, 2, 3...）转换为Excel列字母（A, B, C...Z, AA, AB...）

**解决方案**:
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
col_number_to_letter(28)  # 'AB'
```

---

### 四、查找能力问题

#### 问题4.1: 不知道项目中有哪些能力

**症状**: 需要某个功能，但不知道项目中是否已有实现。

**解决方案**:

**步骤1**: 查看`skills/README.md`的目录结构
```markdown
skills/
├── lark-skills/       # 飞书相关
├── sdet-skills/       # SDET平台相关
└── case-skills/       # 用例处理相关
```

**步骤2**: 按功能查找
| 功能 | Skill位置 |
|------|----------|
| 读取飞书表格 | skills/lark-skills/lark-sheet-reader/ |
| 写入飞书表格 | skills/lark-skills/lark-sheet-writer/ |
| SDET平台接口 | skills/sdet-skills/sdet-api-helper/ |

**步骤3**: 搜索文件名
```bash
# Windows PowerShell
Get-ChildItem -Path skills -Recurse -Filter "*keyword*"

# Linux/Mac
find skills -name "*keyword*"
```

---

### 五、API调用问题

#### 问题5.1: 如何调用飞书API？

**步骤1**: 获取access_token
```python
url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
data = {"app_id": app_id, "app_secret": app_secret}
response = requests.post(url, json=data)
access_token = response.json().get("app_access_token")
```

**步骤2**: 读取表格
```python
url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers)
data = response.json().get("data", {}).get("valueRange", {}).get("values", [])
```

**步骤3**: 写入表格
```python
url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
headers = {"Authorization": f"Bearer {access_token}"}
payload = {
    "valueRange": {
        "range": "sheet_id!A1:A1",
        "values": [["value"]]
    }
}
response = requests.put(url, headers=headers, json=payload)
```

---

### 六、数据处理问题

#### 问题6.1: 飞书表格数据格式复杂

**现象**: 表头或单元格数据是JSON字符串，如：
```python
'[{"segmentStyle": {...}, "text": "测试点编号\\n"}]'
```

**解决方案**:
```python
import json

# 处理复杂类型
for i, cell in enumerate(row):
    if isinstance(cell, (dict, list)):
        cell = json.dumps(cell, ensure_ascii=False)
    row_dict[key] = cell if cell else None
```

#### 问题6.2: 如何查找特定列？

**解决方案**:
```python
def find_column_index(headers, column_name):
    """查找列索引（从1开始）"""
    for i, header in enumerate(headers):
        if isinstance(header, str) and column_name in header:
            return i + 1
    return None

# 使用
case_code_col = find_column_index(headers, '用例编号')
```

---

### 七、调试技巧

#### 技巧7.1: 详细日志输出

```python
print(f"请求URL: {url}")
print(f"Range: {range_str}")
print(f"Value: {value}")
print(f"响应: code={result.get('code')}, msg={result.get('msg')}")
```

#### 技巧7.2: 测试先行

```python
# 测试模式：只执行一条
TEST_MODE = True
if TEST_MODE:
    updates = updates[:1]
```

#### 技巧7.3: 错误记录

```python
import traceback

try:
    # 执行操作
    pass
except Exception as e:
    # 记录详细错误
    with open('error.log', 'w') as f:
        f.write(f'错误: {e}\n\n')
        f.write(traceback.format_exc())
```

---

## 📚 参考资源

- **飞书开放平台**: https://open.feishu.cn/document/server-docs/docs/sheets-v3/
- **表格API文档**: https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-overview
- **Skills使用指南**: `skills/README.md`

---

## 🤝 贡献指南

发现新问题时，请按以下格式添加：

```markdown
### 问题X.X: [问题标题]

**错误现象**:
```
[错误信息或代码]
```

**原因分析**:
[分析原因]

**解决方案**:
```python
[解决方案代码]
```
```

---

**最后更新**: 2026-03-03
