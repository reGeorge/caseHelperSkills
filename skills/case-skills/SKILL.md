---
name: "case-skills"
description: "测试用例相关技能集合，支持用例读取、AI概述生成等功能。Invoke when user needs to work with test cases, including reading from Lark spreadsheets and generating AI summaries."
---

# 测试用例技能集合 (Case Skills Collection)

这是测试用例相关技能的总入口，集成了所有用例操作的技能模块。

## 技能模块概览

本项目包含以下测试用例相关技能：

### 1. **case-ai-overview** - 测试用例AI概述生成器
- **功能**：读取飞书表格中的测试用例，分析后为每条用例生成简洁的AI概述
- **用途**：批量生成用例概述、简化用例描述、自动化用例文档整理
- **依赖**：lark-sheet-reader（用于读取飞书表格）
- **路径**：`case-ai-overview/`

## 技能依赖关系

```
case-skills (总入口)
└── case-ai-overview (AI概述生成)
    ├── 依赖: lark-sheet-reader (飞书表格读取)
    └── 用途: 生成用例AI概述
```

## 典型使用场景

### 场景1：批量生成用例概述
```bash
# 读取飞书表格并生成AI概述
→ 读取指定飞书表格的所有用例
→ 分析每条用例的预置条件、测试步骤、期望结果
→ 生成简洁的一句话概述
→ 输出包含新列的用例数据
```

**推荐流程**：
1. 提供飞书表格URL
2. 配置飞书应用凭证
3. 运行生成脚本
4. 查看生成的概述
5. 导出结果到JSON或回写到表格

## 配置说明

### 必需配置
所有技能都需要以下飞书配置：

```python
config = {
    "app_id": "cli_a83faf50a228900e",    # 飞书应用ID
    "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"  # 飞书应用密钥
}
```

### 表格列名要求
- **用例名称**：测试用例的标题
- **预置条件**：测试前的配置和准备
- **测试步骤**：具体的测试操作步骤
- **期望结果**：预期的测试结果

### 输出列名
- **用例AI概述**：生成的AI概述（默认列名）

## 快速开始

### 安装依赖
```bash
pip install requests
```

### 使用示例

#### 方式1：命令行脚本
```bash
cd case-ai-overview
python read_and_generate.py
```

#### 方式2：Python脚本
```python
from case_ai_overview import CaseAIOverviewGenerator

# 初始化
generator = CaseAIOverviewGenerator(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 从URL读取并生成概述
url = "https://ruijie.feishu.cn/sheets/xxx?sheet=xxx"
cases = generator.generate_from_url(url)

# 预览结果
generator.preview_overviews(cases)

# 保存到文件
generator.save_to_file(cases, "output.json")
```

## AI概述生成规则

概述生成基于以下规则：

### 1. 主要信息来源
- **用例名称**：作为概述的核心
- **预置条件**：提取关键配置信息
- **测试步骤**：提取关键操作
- **期望结果**：提取预期结果

### 2. 特殊操作识别
- **加入黑名单** → "用户被加入黑名单"
- **移除黑名单** → "用户被移除黑名单"
- **首次认证** → "首次认证"
- **非首次认证** → "已学习用户认证"

### 3. 关键配置提取
- "开启自动学习" / "关闭自动学习"
- "是否校验服务器证书" → "校验服务器证书"

### 4. 概述格式
- 使用顿号（、）连接各部分
- 限制长度不超过80字符
- 自动去重和简化

## 示例输出

### 输入示例
```json
{
  "用例名称": "开启证书认证，未学习到本地的证书用户认证成功",
  "预置条件": "1、新增证书身份源\n2、客户端导入证书",
  "测试步骤": "1、开启证书认证\n2、苹果手机首次证书认证",
  "期望结果": "苹果手机证书认证成功"
}
```

### 输出示例
```json
{
  "用例名称": "开启证书认证，未学习到本地的证书用户认证成功",
  "用例AI概述": "开启证书认证、未学习到本地的证书用户认证成功",
  ...
}
```

## 性能说明

- **读取速度**：约100条/秒
- **生成速度**：约1000条/秒
- **批量处理**：支持任意数量用例

## 最佳实践

### 1. 数据准备
- 确保表格第一行是表头
- 列名必须包含"用例名称"、"预置条件"、"测试步骤"、"期望结果"
- 处理空值和异常数据

### 2. 概述优化
- 提供清晰的用例名称
- 确保测试步骤详细
- 明确期望结果

### 3. 质量保证
- 人工审核生成的概述
- 调整生成规则
- 优化关键词提取

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方法 |
|-----|------|---------|
| 读取失败 | 表格权限不足 | 确保应用有表格访问权限 |
| 概述为空 | 列名不匹配 | 检查列名是否正确 |
| 概述不准确 | 用例描述不清 | 优化用例名称和描述 |

## 各技能详细文档

每个技能都有独立的详细文档，请根据需求查看：

1. **case-ai-overview**：`case-ai-overview/SKILL.md`

## 相关Skills

- **lark-skills**：飞书相关技能集合
  - `lark-access-token`：获取飞书API的access_token
  - `lark-sheet-reader`：读取飞书表格内容
  - `lark-sheet-writer`：写入和编辑飞书表格记录

## 版本说明

当前版本：v1.0
- 初始版本，包含1个测试用例技能
- 支持从飞书表格读取用例
- 支持生成AI概述
- 支持批量处理

## 未来规划

- [ ] 支持用例分类和标签
- [ ] 支持用例去重和合并
- [ ] 支持用例优先级分析
- [ ] 支持用例覆盖率分析
