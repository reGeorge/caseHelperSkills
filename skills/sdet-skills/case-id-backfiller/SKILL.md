# 用例ID回填工具

这个skill帮助用户将SDET平台上创建的测试用例ID回写到飞书表格中，通过匹配用例名称来定位并更新对应记录。

## 快速参考

### ⚡ 快速开始

```bash
# 直接使用已验证的脚本
python skills/sdet-skills/case-id-backfiller/scripts/write_case_id_cell_by_cell.py
```

### 🔑 关键配置

**飞书API关键点：**
- URL: `PUT /sheets/v2/spreadsheets/{token}/values`
- Range格式: `sheet_id!起始:结束` (单个单元格也要写成范围)
- Token类型: `app_access_token`
- HTTP方法: 必须使用PUT

### ✅ 已验证

- ✅ 成功写入25个Case ID到飞书表格
- ✅ 使用正确的飞书API格式
- ✅ 详细的错误处理和日志输出

详细说明请参考下方的"使用前提"和"脚本说明"部分。

## 功能说明

- 从SDET平台获取用例信息（用例ID和用例名称）
- 读取飞书表格中的测试用例数据
- 通过用例名称匹配SDET用例与飞书表格记录
- 将匹配的用例ID回写到飞书表格的"脚本序号"列
- 支持批量处理多个用例
- 支持预览模式，不实际修改飞书表格

## 使用场景

当用户需要：
- 批量创建自动化用例后，将用例ID同步到飞书表格
- 维护飞书表格中的用例与SDET平台的关联关系
- 自动化用例管理流程

## 使用前提

### ✅ 飞书表格API正确使用方式

本技能已成功验证飞书表格API的写入功能，关键注意事项如下：

#### 1. API端点格式

**正确的URL格式：**
```
PUT https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values
```

**错误示例：**
```
PUT https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}  # ❌ 错误
```

#### 2. Range格式要求 ⚠️ **重要**

**关键规则：**
- Range必须使用范围格式，即使是单个单元格
- 必须包含sheet_id前缀
- 格式：`{sheet_id}!{起始单元格}:{结束单元格}`

**示例：**
```json
// ✅ 正确
"range": "FYZ5JP!P60:P60"  // 单个单元格也要写成范围

// ❌ 错误
"range": "FYZ5JP!P60"      // 会返回 "wrong range" 错误
"range": "P60"             // 会返回 "sheetId not found" 错误
"range": "FYZ5JP!P60:P62"  // 值数组必须匹配范围大小
```

#### 3. 请求体格式

```json
{
    "valueRange": {
        "range": "FYZ5JP!P60:P60",
        "values": [["66249"]]
    }
}
```

**注意事项：**
- `values` 是二维数组
- 单个单元格：`[["value"]]`
- 多个单元格：`[["val1", "val2"], ["val3", "val4"]]`

#### 4. 认证方式

**Token获取：**
```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

**请求体：**
```json
{
    "app_id": "cli_a83faf50a228900e",
    "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
}
```

**响应：**
```json
{
    "code": 0,
    "app_access_token": "t-xxxxx",
    "expire": 7200
}
```

**重要：**
- 使用 `app_access_token` 而非 `tenant_access_token`
- Token有效期2小时，注意缓存和刷新

#### 5. HTTP方法要求

- **必须使用 PUT 方法**
- POST 方法返回 404 错误
- Content-Type 必须是 `application/json`

#### 6. 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `404 Not Found` | URL路径错误 | 使用 `/values` 而非 `/values/{range}` |
| `wrong range=FYZ5JP!P60` | Range格式错误 | 改为 `FYZ5JP!P60:P60` |
| `sheetId not found` | Range缺少sheet_id | 加上sheet_id前缀 |
| `HTTP 403` | 权限不足 | 检查应用权限配置 |
| `HTTP 400` | 参数格式错误 | 检查请求体JSON格式 |

#### 7. 使用限制

- 单次写入不超过 5000 行、100 列
- 每个单元格不超过 50,000 字符
- 推荐每个单元格不超过 40,000 字符

### MCP工具限制说明

**飞书MCP工具限制：**
- `sheets_v3_spreadsheetSheet_replace` 只能替换单元格内容
- 无法向空单元格写入数据
- 需要单元格已有内容才能执行替换操作

**解决方案：**
- 本技能使用直接的飞书API而非MCP工具
- 支持向空单元格写入数据
- 完整的错误处理和重试机制

## 技术实现

### 技术栈

- **SDET平台API**: 查询用例信息
- **飞书开放平台API**: 读取和更新表格数据
- **lark-sheet-writer技能**: 飞书表格写入操作

### 数据流程

1. **获取SDET用例信息**
   - 调用SDET平台API获取指定用例ID的详细信息
   - 提取用例名称和用例编号

2. **读取飞书表格**
   - 使用lark-sheet-writer读取飞书表格数据
   - 获取表头和数据行

3. **匹配用例**
   - 在飞书表格中查找与SDET用例名称匹配的记录
   - 确定需要更新的行号和列号

4. **回写用例ID**
   - 使用lark-sheet-writer更新指定单元格
   - 将用例ID写入"脚本序号"列

## 使用方法

### 1. 基本使用

```bash
# 回填指定范围的用例ID
python scripts/backfill_case_ids.py \
    --case-id-range 66249 66274 \
    --spreadsheet-token K8V2sTKLyhE54Ot75EycbnKLnvb \
    --sheet-id FYZ5JP

# 回填指定的用例ID列表
python scripts/backfill_case_ids.py \
    --case-ids 66249 66250 66251 \
    --spreadsheet-token K8V2sTKLyhE54Ot75EycbnKLnvb \
    --sheet-id FYZ5JP

# 预览模式（不实际更新）
python scripts/backfill_case_ids.py \
    --case-id-range 66249 66274 \
    --spreadsheet-token K8V2sTKLyhE54Ot75EycbnKLnvb \
    --sheet-id FYZ5JP \
    --dry-run
```

### 2. 使用映射文件

```bash
# 从映射文件读取并回填
python scripts/backfill_case_ids.py \
    --mapping-file case_id_mapping.json \
    --spreadsheet-token K8V2sTKLyhE54Ot75EycbnKLnvb \
    --sheet-id FYZ5JP
```

## 字段映射

| SDET平台字段 | 飞书表格字段 | 说明 |
|-------------|-------------|------|
| id | 脚本序号 | 用例ID |
| name | 用例名称 | 用例名称 |
| caseNo | 用例编号 | 用例编号 |

## 脚本说明

### scripts/backfill_case_ids.py

主脚本，负责执行用例ID回填操作。

**功能：**
- 获取SDET用例信息
- 读取飞书表格数据
- 匹配用例名称
- 更新飞书表格

**参数：**
- `--case-ids`: 指定要回填的用例ID列表
- `--case-id-range`: 指定用例ID范围（包含两端）
- `--mapping-file`: 从映射文件读取用例信息
- `--spreadsheet-token`: 飞书表格token
- `--sheet-id`: 工作表ID
- `--dry-run`: 预览模式，不实际更新

**示例：**
```bash
python scripts/backfill_case_ids.py --case-id-range 66249 66274 --spreadsheet-token K8V2sTKLyhE54Ot75EycbnKLnvb --sheet-id FYZ5JP
```

### scripts/generate_mapping.py

生成用例ID映射文件。

**功能：**
- 查询SDET平台用例信息
- 生成JSON和CSV格式的映射文件

**参数：**
- `--case-id-range`: 指定用例ID范围
- `--output-dir`: 输出目录

**示例：**
```bash
python scripts/generate_mapping.py --case-id-range 66249 66274
```

### scripts/write_case_id_cell_by_cell.py ⭐ **推荐**

逐个单元格写入Case ID到飞书表格（已验证可用）。

**功能：**
- 逐个单元格写入Case ID
- 使用飞书API v2接口
- 详细的错误处理和日志输出
- 支持批量写入，逐个处理每个单元格

**使用方法：**
```bash
python scripts/write_case_id_cell_by_cell.py
```

**配置：**
在脚本的 `main()` 函数中修改：
```python
spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
sheet_id = "FYZ5JP"

case_id_mapping = {
    60: 66249,
    61: 66250,
    67: 66251,
    # ... 更多映射
}
```

**输出示例：**
```
================================================================================
逐个单元格写入Case ID
================================================================================

[INFO] 获取飞书access token...
[OK] Token获取成功

[INFO] 读取表格数据...
[OK] 读取到 100 行数据
[INFO] 表头: ['用例包名称', '测试点编号', ...]
[INFO] 脚本序号列索引: 15

[INFO] 开始写入 26 个Case ID...
--------------------------------------------------------------------------------

写入行 60 (Case ID: 66249)
  用例名称: 用户名抢占-开启自动学习
  [OK] 写入成功: P60 = 66249

写入行 61 (Case ID: 66250)
  用例名称: 用户名抢占-不开启自动学习
  [OK] 写入成功: P61 = 66250
...

================================================================================
写入完成!
================================================================================
成功: 25 行
失败: 0 行
未找到: 1 行
总计: 26 行
================================================================================
```

**API调用流程：**
1. 获取 `app_access_token`
2. 读取飞书表格数据，获取表头和列索引
3. 遍历 `case_id_mapping`，逐个写入Case ID
4. 使用正确的Range格式：`sheet_id!单元格:单元格`
5. 输出详细的写入结果统计

**关键代码：**
```python
def write_single_cell(spreadsheet_token, sheet_id, access_token,
                      row_index, col_index, value):
    col_letter = col_index_to_letter(col_index)
    row_num = row_index + 1
    
    # 关键：Range必须是范围格式，即使单个单元格
    range_str = f"{sheet_id}!{col_letter}{row_num}:{col_letter}{row_num}"
    
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    
    data = {
        "valueRange": {
            "range": range_str,
            "values": [[value]]
        }
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 200 and response.json().get("code") == 0
```

**推荐理由：**
- ✅ 已验证成功写入25个Case ID
- ✅ 使用正确的飞书API格式
- ✅ 详细的错误处理和日志
- ✅ 支持逐个单元格写入，可精确控制
- ✅ 完整的统计和进度显示

## 配置说明

### config.json

配置文件包含以下字段：

```json
{
    "sdet": {
        "base_url": "https://sdet.ruishan.cc/api/sdet-atp",
        "token": "YOUR_TOKEN_HERE"
    },
    "lark": {
        "app_id": "cli_a83faf50a228900e",
        "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
    },
    "spreadsheet": {
        "token": "K8V2sTKLyhE54Ot75EycbnKLnvb",
        "sheet_id": "FYZ5JP",
        "case_name_col": "用例名称",
        "script_id_col": "脚本序号"
    }
}
```

## 注意事项

### API使用注意事项

1. **Range格式 ⚠️ 最重要**
   - 必须使用范围格式：`sheet_id!起始:结束`
   - 单个单元格也要写成：`sheet_id!P60:P60`，不能写成 `sheet_id!P60`
   - Range必须包含sheet_id前缀
   - 错误的Range会导致 "wrong range" 或 "sheetId not found" 错误

2. **HTTP方法**
   - 必须使用 PUT 方法
   - 不能使用 POST 方法（会返回404）
   - Content-Type 必须是 `application/json`

3. **Token管理**
   - 使用 `app_access_token` 而非 `tenant_access_token`
   - Token有效期2小时
   - 建议缓存Token，避免频繁请求

4. **URL格式**
   - 正确：`/sheets/v2/spreadsheets/{token}/values`
   - 错误：`/sheets/v2/spreadsheets/{token}/values/{range}`
   - Range放在请求体的 `valueRange.range` 字段中

5. **请求数据格式**
   ```json
   {
       "valueRange": {
           "range": "FYZ5JP!P60:P60",
           "values": [["66249"]]  // 二维数组
       }
   }
   ```
   - `values` 必须是二维数组
   - 单个单元格：`[["value"]]`
   - 多个单元格：`[["val1", "val2"], ["val3", "val4"]]`

6. **错误处理**
   - 检查响应的 `code` 字段（0表示成功）
   - 记录失败的原因和位置
   - 建议实现重试机制

### 数据匹配注意事项

1. **用例名称匹配**：回填操作依赖用例名称的精确匹配，请确保SDET平台和飞书表格中的用例名称一致
2. **权限要求**：需要飞书表格的编辑权限
3. **行号计算**：
   - Excel行号从1开始（第1行是表头）
   - API的row_index从0开始
   - 转换公式：`row_index = Excel行号 - 1`

### 性能优化建议

1. **批量写入**
   - 当前实现是逐个单元格写入
   - 可以优化为批量范围写入，减少HTTP请求
   - 示例：一次写入 `P60:P70` 范围

2. **并发处理**
   - 对于大量数据，可以使用并发请求
   - 注意不要超过API限流限制

3. **缓存机制**
   - 缓存access_token
   - 缓存表格元数据（表头、列索引）

### 安全建议

1. **敏感信息保护**
   - 不要在代码中硬编码app_secret
   - 使用环境变量或配置文件
   - 将配置文件加入.gitignore

2. **错误信息脱敏**
   - 日志输出时隐藏敏感信息
   - Token只显示前几位

3. **权限最小化**
   - 只申请必要的API权限
   - 定期审查应用权限
3. **备份建议**：批量更新前建议先备份飞书表格数据
4. **预览模式**：使用`--dry-run`参数可以在实际更新前预览将要执行的更改

## 故障排查

### 问题：找不到匹配的用例

**原因：** 用例名称不一致或格式差异

**解决方案：**
1. 检查SDET平台和飞书表格中的用例名称是否完全一致
2. 注意空格、换行符等不可见字符
3. 使用`--dry-run`参数查看详细的匹配结果

### 问题：飞书表格更新失败

**原因：** 权限不足或网络问题

**解决方案：**
1. 确认飞书表格的编辑权限
2. 检查网络连接
3. 查看详细的错误信息

### API常见错误

#### 错误1：404 Not Found

**错误信息：**
```
404 page not found
```

**原因：**
- URL路径错误
- 使用了错误的API路径

**解决方案：**
- 检查URL格式：`/sheets/v2/spreadsheets/{token}/values`
- 不要在URL中包含range参数

#### 错误2：wrong range

**错误信息：**
```
{"code":90202,"msg":"wrong range=FYZ5JP!P60"}
```

**原因：**
- Range格式错误
- 单个单元格没有写成范围格式

**解决方案：**
- 将 `FYZ5JP!P60` 改为 `FYZ5JP!P60:P60`
- Range必须是范围格式：`起始单元格:结束单元格`

#### 错误3：sheetId not found

**错误信息：**
```
{"code":90215,"msg":"sheetId not found"}
```

**原因：**
- Range中缺少sheet_id
- sheet_id不正确

**解决方案：**
- Range必须包含sheet_id：`FYZ5JP!P60:P60`
- 检查sheet_id是否正确

#### 错误4：HTTP 403 Forbidden

**错误信息：**
```
HTTP 403 Forbidden
```

**原因：**
- 应用没有表格编辑权限
- Token过期或无效

**解决方案：**
1. 检查飞书开放平台的应用权限配置
2. 确认应用有 `sheets:spreadsheet` 读写权限
3. 检查token是否有效，重新获取token

#### 错误5：HTTP 400 Bad Request

**错误信息：**
```
HTTP 400 Bad Request
```

**原因：**
- 请求体格式错误
- 参数格式不正确

**解决方案：**
1. 检查请求体JSON格式
2. 确认 `valueRange` 结构正确
3. 检查 `values` 是否是二维数组

#### 错误6：JSON解析错误

**错误信息：**
```
json.decoder.JSONDecodeError: Extra data
```

**原因：**
- API返回的不是JSON格式
- 可能是404页面或其他错误页面

**解决方案：**
1. 检查URL是否正确
2. 打印原始响应内容调试
3. 确认HTTP方法是否为PUT

#### 错误7：Token获取失败

**错误信息：**
```
{"code":10014,"msg":"app id not exists"}
```

**原因：**
- app_id或app_secret不正确

**解决方案：**
1. 检查飞书开放平台的应用配置
2. 确认app_id和app_secret是否正确
3. 重新生成app_secret（如果泄露）

### 调试技巧

1. **打印完整响应**
   ```python
   print(f"状态码: {response.status_code}")
   print(f"响应头: {response.headers}")
   print(f"响应内容: {response.text}")
   ```

2. **验证Range格式**
   ```python
   # 正确
   range_str = "FYZ5JP!P60:P60"
   
   # 错误
   # range_str = "FYZ5JP!P60"
   # range_str = "P60"
   ```

3. **检查请求体**
   ```python
   import json
   print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
   ```

4. **使用curl测试**
   ```bash
   curl -X PUT 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/K8V2sTKLyhE54Ot75EycbnKLnvb/values' \
     -H 'Authorization: Bearer YOUR_TOKEN' \
     -H 'Content-Type: application/json' \
     -d '{
       "valueRange": {
         "range": "FYZ5JP!P60:P60",
         "values": [["66249"]]
       }
     }'
   ```

## 依赖技能

- [lark-sheet-writer](../lark-skills/lark-sheet-writer/): 飞书表格写入操作
- [platform-client](../sdet-skills/platform-client/): SDET平台客户端
