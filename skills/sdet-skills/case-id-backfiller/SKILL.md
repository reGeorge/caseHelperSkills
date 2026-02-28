---
name: "case-id-backfiller"
description: "匹配SDET用例ID与飞书表格用例名称，并将用例ID回写到飞书表格的脚本序号列。Invoke when user needs to sync SDET test case IDs back to Feishu spreadsheet after batch creation."
---

# 用例ID回填工具

这个skill帮助用户将SDET平台上创建的测试用例ID回写到飞书表格中，通过匹配用例名称来定位并更新对应记录。

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

### ⚠️ 飞书表格写入限制

目前飞书表格API的写入操作存在以下限制：

1. **API权限限制**
   - 飞书开放平台的表格写入API可能需要特定权限配置
   - 应用需要拥有表格的 `sheets:spreadsheet:write` 权限
   - 部分API路径（如 `/values` 接口）可能已弃用或不可用

2. **MCP工具限制**
   - 飞书MCP提供的 `sheets_v3_spreadsheetSheet_replace` 只能替换单元格内容
   - 无法直接向空单元格写入数据
   - 需要单元格已有内容才能执行替换操作

3. **lark-sheet-writer限制**
   - `update_record` 方法报告更新成功，但实际未写入数据
   - 可能是API权限或网络问题导致

### 当前状态

由于上述限制，自动写入功能暂不可用。建议使用以下方案：

#### 方案1：手动更新（推荐）
直接在飞书表格中根据映射关系手动填入Case ID

#### 方案2：使用生成的映射文件
- `case_id_mapping.json`：JSON格式映射
- `case_id_mapping.csv`：CSV格式映射（可导入Excel）
- `update_mapping.json`：详细映射信息

#### 方案3：检查飞书应用权限
1. 前往飞书开放平台
2. 检查应用 `cli_a83faf50a228900e` 的权限配置
3. 确认表格写入权限已开通
4. 重新授权应用访问该表格

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

1. **用例名称匹配**：回填操作依赖用例名称的精确匹配，请确保SDET平台和飞书表格中的用例名称一致
2. **权限要求**：需要飞书表格的编辑权限
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

## 依赖技能

- [lark-sheet-writer](../lark-skills/lark-sheet-writer/): 飞书表格写入操作
- [platform-client](../sdet-skills/platform-client/): SDET平台客户端
