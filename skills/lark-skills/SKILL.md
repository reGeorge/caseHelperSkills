# 飞书技能集合 (Lark Skills Collection)

这是飞书相关技能的总入口，集成了所有飞书API操作的技能模块。通过这个技能，你可以完整地使用飞书平台的各种功能。

## 技能模块概览

本项目包含以下飞书相关技能：

### 1. **lark-access-token** - 飞书Access Token获取器
- **功能**：获取飞书API的access_token
- **用途**：为所有飞书API调用提供认证凭证
- **依赖**：无
- **路径**：`lark-access-token/`

### 2. **lark-sheets** - 飞书表格管理器
- **功能**：获取飞书表格的工作表列表和信息
- **用途**：查询和管理飞书表格的工作表
- **依赖**：lark-access-token
- **路径**：`lark-sheets/`

### 3. **lark-sheet-reader** - 飞书表格内容读取器
- **功能**：读取飞书表格内容并转换为JSON格式
- **用途**：导出测试用例、读取表格数据、批量获取信息
- **依赖**：lark-access-token, lark-sheets
- **路径**：`lark-sheet-reader/`

### 4. **lark-sheet-writer** - 飞书表格记录写入器
- **功能**：写入和编辑飞书表格记录
- **用途**：添加新记录、更新现有记录、批量导入数据
- **依赖**：lark-access-token, lark-sheets
- **路径**：`lark-sheet-writer/`

### 5. **lark-api-helper** - 飞书API综合助手
- **功能**：提供飞书API的完整操作支持，包含以上所有功能
- **用途**：一站式飞书API操作，简化开发流程
- **依赖**：无（内部集成了其他技能）
- **路径**：`lark-api-helper/`

## 技能依赖关系

```
lark-skills (总入口)
├── lark-access-token (基础认证)
│   └── 被: lark-sheets, lark-sheet-reader, lark-sheet-writer
│
├── lark-sheets (表格管理)
│   ├── 依赖: lark-access-token
│   └── 被: lark-sheet-reader, lark-sheet-writer
│
├── lark-sheet-reader (表格读取)
│   ├── 依赖: lark-access-token, lark-sheets
│   └── 用途: 读取数据、导出JSON
│
├── lark-sheet-writer (表格写入)
│   ├── 依赖: lark-access-token, lark-sheets
│   └── 用途: 写入数据、更新记录
│
└── lark-api-helper (综合助手)
    ├── 集成: lark-access-token, lark-sheets
    └── 用途: 一站式API操作
```

## 典型使用场景

### 场景1：读取飞书表格中的测试用例
```bash
# 使用 lark-access-token 获取认证
→ 使用 lark-sheets 获取工作表列表
→ 使用 lark-sheet-reader 读取数据并导出JSON
```

**推荐流程**：
1. 配置 `app_id` 和 `app_secret`
2. 获取 `access_token`
3. 查询表格的 `spreadsheet_token` 和 `sheet_id`
4. 读取表格内容
5. 导出为JSON格式

### 场景2：向飞书表格添加新测试用例
```bash
# 使用 lark-access-token 获取认证
→ 使用 lark-sheets 获取工作表信息
→ 使用 lark-sheet-writer 写入新记录
```

**推荐流程**：
1. 配置 `app_id` 和 `app_secret`
2. 获取 `access_token`
3. 确认目标 `sheet_id`
4. 准备测试用例数据（JSON格式）
5. 写入到表格

### 场景3：更新飞书表格中的现有记录
```bash
# 使用 lark-access-token 获取认证
→ 使用 lark-sheet-reader 查找记录
→ 使用 lark-sheet-writer 更新记录
```

**推荐流程**：
1. 读取现有数据
2. 定位需要更新的记录
3. 准备更新数据
4. 执行更新操作

### 场景4：一站式API操作（推荐新手使用）
```bash
# 直接使用 lark-api-helper
→ 内部自动处理所有依赖和流程
```

## 配置说明

### 必需配置
所有技能都需要以下基础配置：

```python
config = {
    "app_id": "cli_xxxxxxxxx",        # 飞书应用ID
    "app_secret": "xxxxxxxxxxxxxxxx"  # 飞书应用密钥
}
```

### 获取配置信息
1. 登录飞书开放平台：https://open.feishu.cn/
2. 创建或选择一个应用
3. 在应用凭证页面获取 `app_id` 和 `app_secret`
4. 开启必要的权限（如 `sheets:spreadsheet` 等）

### 可选配置
- `spreadsheet_token`: 表格token（可从表格URL获取）
- `sheet_id`: 工作表ID
- `access_token`: 访问令牌（可自动获取）

## API端点汇总

### 认证端点
```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

### 表格端点
```
GET  https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update
```

## 权限要求

确保飞书应用已开通以下权限：

| 权限名称 | 权限码 | 用途 |
|---------|--------|------|
| 表格访问权限 | `sheets:spreadsheet` | 访问飞书表格 |
| 表格只读权限 | `sheets:spreadsheet.readonly` | 读取表格数据 |
| 表格读写权限 | `sheets:spreadsheet.readwrite` | 写入和修改数据 |

## 快速开始

### 安装依赖
```bash
pip install requests
```

### 选择使用方式

#### 方式1：使用独立技能（推荐有经验的用户）
根据需求选择对应的技能模块，参考各自的 SKILL.md 文档。

#### 方式2：使用综合助手（推荐新手）
使用 `lark-api-helper` 技能，它集成了所有功能，使用更简单。

### 示例代码

#### 读取表格
```python
from lark_sheet_reader import LarkSheetReader

reader = LarkSheetReader(
    app_id="your_app_id",
    app_secret="your_app_secret",
    spreadsheet_token="your_token"
)

data = reader.read_sheet(sheet_id="your_sheet_id")
print(data.to_json())
```

#### 写入表格
```python
from lark_sheet_writer import LarkSheetWriter

writer = LarkSheetWriter(
    app_id="your_app_id",
    app_secret="your_app_secret",
    spreadsheet_token="your_token"
)

record = {"用例名称": "测试", "用例描述": "描述"}
result = writer.write_record(sheet_id="your_sheet_id", record=record)
```

## 最佳实践

### 1. Token管理
- 定期刷新access_token（有效期为2小时）
- 使用缓存减少API调用
- 不要硬编码token到代码中

### 2. 错误处理
- 检查API响应状态码
- 处理网络异常
- 记录错误日志

### 3. 性能优化
- 批量操作减少API调用
- 合理使用缓存
- 处理分页数据

### 4. 安全性
- 使用环境变量存储敏感信息
- 不要在代码中硬编码凭证
- 限制应用权限范围

## 故障排除

### 常见问题

| 错误 | 原因 | 解决方法 |
|-----|------|---------|
| 401 Unauthorized | access_token无效或过期 | 重新获取token |
| 403 Forbidden | 应用权限不足 | 检查并开通权限 |
| 404 Not Found | 资源不存在 | 检查token和sheet_id |
| 429 Too Many Requests | API调用频率过高 | 减少调用频率 |

## 各技能详细文档

每个技能都有独立的详细文档，请根据需求查看：

1. **lark-access-token**：`lark-access-token/SKILL.md`
2. **lark-sheets**：`lark-sheets/SKILL.md`
3. **lark-sheet-reader**：`lark-sheet-reader/SKILL.md`
4. **lark-sheet-writer**：`lark-sheet-writer/SKILL.md`
5. **lark-api-helper**：`lark-api-helper/SKILL.md`

## 相关资源

- 飞书开放平台：https://open.feishu.cn/
- 飞书API文档：https://open.feishu.cn/document/server-docs/docs/server-docs
- 飞书表格API：https://open.feishu.cn/document/server-docs/docs/docs/sheets-v3

## 注意事项

- access_token有有效期（通常2小时），过期后需要重新获取
- 请妥善保管app_secret和access_token
- 遵守飞书API调用频率限制
- 确保网络连接稳定
- 处理API返回的错误信息
- 建议在测试环境中验证操作后再应用到生产环境

## 版本说明

当前版本：v1.0
- 初始版本，包含5个飞书相关技能
- 支持飞书表格的读写操作
- 提供完整的API操作支持
