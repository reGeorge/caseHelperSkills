---
name: "case-ai-overview"
description: "读取飞书表格中的测试用例，分析后为每条用例生成AI概述列。Invoke when user needs to analyze test cases and generate concise summaries."
---

# 测试用例AI概述生成器

这个skill帮助用户读取飞书表格中的测试用例，并使用AI为每条用例生成简洁的概述。

## 功能说明

- 读取飞书表格中的测试用例数据
- 分析每条用例的预置条件、测试步骤、期望结果
- 使用AI生成一句话的用例概述
- 将概述添加到表格的新列中
- 支持批量处理大量用例

## 使用场景

当用户需要：
- 批量生成测试用例的概述
- 简化用例描述，提高可读性
- 自动化用例文档整理
- 生成用例报告摘要

## 使用方法

### 1. 基本使用

```python
from case_ai_overview import CaseAIOverviewGenerator

# 初始化生成器
generator = CaseAIOverviewGenerator(
    app_id="your_app_id",
    app_secret="your_app_secret",
    spreadsheet_token="your_token",
    sheet_id="your_sheet_id"
)

# 读取用例并生成概述
result = generator.generate_overviews()

# 保存到表格
generator.save_to_sheet(result)
```

### 2. 从URL读取

```python
# 从飞书表格URL直接读取
url = "https://ruijie.feishu.cn/sheets/xxx?sheet=xxx"
generator = CaseAIOverviewGenerator(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
result = generator.generate_from_url(url)
```

### 3. 自定义列名

```python
# 指定AI概述列名
result = generator.generate_overviews(
    ai_overview_column="用例AI概述"  # 默认列名
)
```

## 参数说明

### 必需参数
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥
- `spreadsheet_token`: 表格token（或通过URL自动获取）
- `sheet_id`: 工作表ID（或通过URL自动获取）

### 可选参数
- `ai_overview_column`: AI概述列名（默认："用例AI概述"）
- `case_name_column`: 用例名称列名（默认："用例名称"）
- `precondition_column`: 预置条件列名（默认："预置条件"）
- `steps_column`: 测试步骤列名（默认："测试步骤"）
- `expected_result_column`: 期望结果列名（默认："期望结果"）

## AI概述生成规则

概述将根据以下信息生成：
1. **用例名称**：主要功能点
2. **预置条件**：前置状态或配置
3. **测试步骤**：关键操作
4. **期望结果**：预期输出或行为

### 示例

**输入**：
- 用例名称：开启自动学习-已学习到本地的证书用户被加入黑名单则认证失败
- 预置条件：1、开启证书认证 2、UNC存在组root\A\AA
- 测试步骤：1、安卓手机导入证书 2、开启证书用户自动学习... 5、再次证书认证
- 期望结果：5、证书认证失败，提示用户已被加入黑名单

**输出**：
- 用例AI概述：开启证书认证，开启自动学习，已学习到本地的用户被加入黑名单后再次认证失败

## 配置要求

### 依赖库
```bash
pip install requests openai
```

### 权限要求
确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readwrite`: 读写权限

## API端点

### 认证
```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

### 表格操作
```
GET  https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}
POST https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update
```

## 使用示例

### 命令行使用

```bash
# 读取表格并生成概述
python case_ai_overview.py \
  --app-id "your_app_id" \
  --app-secret "your_app_secret" \
  --url "https://ruijie.feishu.cn/sheets/xxx?sheet=xxx"

# 保存到新表格
python case_ai_overview.py \
  --app-id "your_app_id" \
  --app-secret "your_app_secret" \
  --url "xxx" \
  --save-to-sheet
```

### Python脚本使用

```python
from case_ai_overview import CaseAIOverviewGenerator

# 配置
config = {
    "app_id": "cli_a83faf50a228900e",
    "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
}

# 读取并生成概述
generator = CaseAIOverviewGenerator(**config)
result = generator.generate_from_url(
    "https://ruijie.feishu.cn/sheets/xxx?sheet=xxx"
)

# 打印结果
for case in result:
    print(f"用例名称: {case['用例名称']}")
    print(f"AI概述: {case['用例AI概述']}")
    print("-" * 60)

# 保存到表格
generator.save_to_sheet(result)
```

## 输出格式

### JSON输出示例

```json
[
  {
    "用例名称": "开启证书认证-未学习到本地的证书用户认证成功",
    "用例AI概述": "开启证书认证，未学习到本地的证书用户首次认证成功",
    "预置条件": "1、新增证书身份源...",
    "测试步骤": "1、开启证书认证 2、苹果手机首次证书认证",
    "期望结果": "2、苹果手机证书认证成功"
  },
  {
    "用例名称": "开启证书认证-已学习到本地的证书用户认证成功",
    "用例AI概述": "开启证书认证，已学习到本地的证书用户再次认证成功",
    "预置条件": "1、新增证书身份源...",
    "测试步骤": "1、开启证书认证 2、苹果手机非首次证书认证",
    "期望结果": "2、苹果手机证书认证成功"
  }
]
```

## 数据处理流程

1. **读取表格数据**
   - 获取access_token
   - 读取指定工作表的所有数据
   - 识别表头和列

2. **AI分析**
   - 提取用例名称、预置条件、测试步骤、期望结果
   - 调用AI模型生成概述
   - 格式化概述文本

3. **添加概述列**
   - 在表格中新增"用例AI概述"列
   - 为每条用例填充生成的概述

4. **保存结果**
   - 批量更新表格数据
   - 返回处理结果

## 注意事项

- 确保表格第一行是表头
- 用例数据必须包含用例名称、预置条件、测试步骤、期望结果等字段
- AI概述会覆盖现有"用例AI概述"列的数据（如果存在）
- 批量处理大量用例时可能需要较长时间
- 建议先在测试表格中验证效果

## 高级功能

### 1. 自定义AI模型

```python
# 使用自定义AI模型
generator = CaseAIOverviewGenerator(
    app_id="your_app_id",
    app_secret="your_app_secret",
    ai_model="gpt-4"  # 默认使用gpt-3.5-turbo
)
```

### 2. 批量处理

```python
# 分批处理，避免API限流
result = generator.generate_overviews(batch_size=10)
```

### 3. 只生成不保存

```python
# 只生成概述，不保存到表格
result = generator.generate_overviews()
# 手动保存到文件
generator.save_to_file(result, "cases_with_overview.json")
```

## 最佳实践

1. **数据准备**
   - 确保用例数据完整
   - 检查列名是否正确
   - 处理空值和异常数据

2. **AI优化**
   - 提供清晰的用例描述
   - 确保测试步骤详细
   - 明确期望结果

3. **性能优化**
   - 使用批量处理
   - 合理设置批次大小
   - 缓存AI结果

4. **质量保证**
   - 人工审核生成的概述
   - 调整AI提示词
   - 优化生成规则

## 错误处理

### 常见错误

1. **表格不存在**
   - 检查URL和token是否正确

2. **权限不足**
   - 确认应用有读写权限

3. **列名不匹配**
   - 检查列名是否与实际表格一致

4. **AI调用失败**
   - 检查API密钥和额度
   - 重试机制

## 故障排除

### 概述不准确
- 调整AI提示词
- 提供更详细的输入信息
- 人工审核和修正

### 处理速度慢
- 减少批次大小
- 使用更快的AI模型
- 并行处理

### 权限错误
- 检查应用权限设置
- 重新获取access_token

## 相关Skills

- `lark-access-token`: 获取飞书API的access_token
- `lark-sheet-reader`: 读取飞书表格内容
- `lark-sheet-writer`: 写入和编辑飞书表格记录
