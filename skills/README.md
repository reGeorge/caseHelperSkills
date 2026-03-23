# Skills 能力库使用指南

## 📚 Skills 概述

Skills是项目的核心能力库，封装了各种可复用的功能和工具。

## 🗂️ Skills 目录结构

```
skills/
├── lark-skills/              # 飞书相关能力
│   ├── lark-access-token/    # 获取访问令牌
│   ├── lark-api-helper/      # API辅助工具
│   ├── lark-sheet-reader/    # 读取飞书表格
│   ├── lark-sheet-writer/    # 写入飞书表格
│   └── lark-sheets/          # 表格操作封装
│
├── sdet-skills/              # SDET测试平台相关能力
│   ├── sdet-api-helper/      # API接口帮助
│   ├── sdet-login/           # 登录认证
│   ├── batch-case-creator/   # 批量创建用例
│   ├── platform-client/      # 平台API客户端封装
│   ├── case-id-backfiller/   # 用例ID回写飞书
│   └── case-debugger/        # 用例调试与偏差修复
│
└── case-skills/              # 用例处理能力
    └── ...
```

## 🔧 Skills 自动发现和推荐系统

项目内置了智能的 skills 发现和推荐系统,帮助你快速找到合适的 skill。

### 核心组件

#### 1. SkillsDiscovery - Skills 发现工具

自动扫描 `skills/` 目录,索引所有可用的技能。

```python
from skills_discovery import SkillsDiscovery

# 初始化
discovery = SkillsDiscovery()

# 搜索
results = discovery.search("飞书", limit=5)

# 按分类获取
lark_skills = discovery.get_by_category("lark-skills")

# 获取所有分类
categories = discovery.list_categories()
```

#### 2. SkillsAssistant - 智能推荐助手

根据需求智能推荐合适的 skills。

```python
from skills_assistant import SkillsAssistant

# 初始化
assistant = SkillsAssistant()

# 智能推荐
recommendations = assistant.interactive_recommend("批量创建测试用例到SDET平台")
print(recommendations)
```

### 特性

- **自动索引**: 自动扫描 skills 目录,无需手动维护
- **智能搜索**: 支持关键词搜索,按相关度排序
- **意图识别**: 识别用户需求,自动推荐合适的 skills
- **多维度匹配**: 基于 ID、名称、描述、关键词、能力等多维度匹配
- **使用指导**: 提供使用提示和代码示例

### 使用场景

1. **不确定需要哪个 skill?** → 使用 SkillsAssistant 智能推荐
2. **想浏览所有技能?** → 使用 SkillsDiscovery.list_categories()
3. **按功能查找?** → 使用 SkillsDiscovery.search()
4. **学习如何使用?** → 查看推荐结果的使用提示

## 🔍 如何查找需要的能力

### 方法1: 使用 SkillsAssistant 智能推荐 (推荐)

使用内置的智能推荐系统,根据需求自动匹配合适的skills:

```python
from skills_assistant import SkillsAssistant

# 初始化助手
assistant = SkillsAssistant()

# 智能推荐
recommendations = assistant.interactive_recommend("我想读取飞书表格中的测试用例数据")
print(recommendations)

# 示例输出:
# # 根据需求推荐Skills
#
# **您的需求**: 我想要读取飞书表格中的测试用例数据
#
# ## 推荐结果 (2个)
#
# ### 1. 飞书表格内容读取器
# **置信度**: 92%
# **路径**: `skills/lark-skills/lark-sheet-reader`
#
# **推荐理由**: 名称匹配'飞书'; 关键词匹配: 飞书, 表格, 读取; 适用场景: 读取测试用例表格
# **使用提示**: 位置: lark-skills/lark-sheet-reader | 场景: 读取测试用例表格 | 主文件: lark_sheet_reader.py | 类名: LarkSheetReader
```

### 方法2: 按功能分类查找

| 功能需求 | 对应Skill | 位置 |
|---------|----------|------|
| 读取飞书表格 | lark-sheet-reader | `skills/lark-skills/lark-sheet-reader/` |
| 写入飞书表格 | lark-sheet-writer | `skills/lark-skills/lark-sheet-writer/` |
| 获取飞书Token | lark-access-token | `skills/lark-skills/lark-access-token/` |
| SDET平台接口 | sdet-api-helper | `skills/sdet-skills/sdet-api-helper/` |
| SDET登录认证 | sdet-login | `skills/sdet-skills/sdet-login/` |
| 批量创建用例 | batch-case-creator | `skills/sdet-skills/batch-case-creator/` |
| 用例调试审计 | case-debugger | `skills/sdet-skills/case-debugger/` |
| 平台API封装 | platform-client | `skills/sdet-skills/platform-client/` |
| 用例ID回写 | case-id-backfiller | `skills/sdet-skills/case-id-backfiller/` |

### 方法3: 搜索文件名

```bash
# Windows PowerShell
Get-ChildItem -Path skills -Recurse -Filter "*writer*"

# Linux/Mac
find skills -name "*writer*"
```

### 方法4: 搜索关键词

```bash
# Windows PowerShell
Get-ChildItem -Path skills -Recurse -Filter "*.py" | Select-String "keyword"

# Linux/Mac
grep -r "keyword" skills/
```

### 方法5: 使用 SkillsDiscovery 工具

```python
from skills_discovery import SkillsDiscovery

# 初始化发现工具
discovery = SkillsDiscovery()

# 搜索skills
results = discovery.search("飞书")
for skill in results:
    print(f"- {skill.name}: {skill.description}")

# 按分类浏览
for category in discovery.list_categories():
    print(f"\n{category}:")
    for skill in discovery.get_by_category(category):
        print(f"  - {skill.name}")
```

## 📖 如何使用Skill

### 示例1: 读取飞书表格

```python
import sys
sys.path.insert(0, 'skills/lark-skills/lark-sheet-reader')
from lark_sheet_reader import LarkSheetReader

# 初始化
reader = LarkSheetReader(app_id, app_secret)

# 从URL读取
data = reader.read_from_url('https://ruijie.feishu.cn/sheets/xxx?sheet=xxx')

# 保存到文件
reader.save_to_file(data, 'output.json')
```

### 示例2: 写入飞书表格

```python
import sys
sys.path.insert(0, 'skills/lark-skills/lark-sheet-writer')
from lark_sheet_writer import LarkSheetWriter

# 初始化
writer = LarkSheetWriter(app_id, app_secret)

# 获取token
access_token = writer.get_access_token()

# 写入数据
range_str = "sheet_id!A1:A1"  # 注意格式
writer._write_range(spreadsheet_token, range_str, [["value"]], access_token)
```

### 示例3: 使用SDET API

```python
import sys
sys.path.insert(0, 'skills/sdet-skills/sdet-api-helper')
from sdet_api_info import _client

# 查询用例
case_detail = _client.get_case_detail(case_id)

# 查询步骤
flows = _client.get_case_flows(case_id)

# 触发调试
log_id = _client.trigger_case_debug(case_id)
```

## 🛠️ Skill开发规范

### 1. 目录结构
```
skill-name/
├── skill_name.py      # 主文件
├── SKILL.md           # 使用说明
├── TROUBLESHOOTING.md # 问题记录
└── README.md          # 概述
```

### 2. 文档要求
- **SKILL.md**: 详细的使用说明、参数说明、示例代码
- **TROUBLESHOOTING.md**: 遇到的问题和解决方案
- **README.md**: 简要说明和快速开始

### 3. 代码规范
- 提供清晰的帮助文档字符串
- 使用类封装主要功能
- 提供命令行接口（如果适用）
- 记录关键日志

## 🚨 常见问题

### Q1: 如何知道项目中有哪些能力？

**A**: 查看本文件（`skills/README.md`）的目录结构部分，或浏览各skill的README。

### Q2: 如何快速找到某个功能？

**A**: 
1. 先看本文件的"按功能分类查找"表格
2. 使用文件搜索（方法2或方法3）
3. 查看skill目录下的README.md

### Q3: 使用skill时遇到错误怎么办？

**A**: 
1. 查看该skill下的`TROUBLESHOOTING.md`
2. 查看日志输出
3. 检查参数格式和类型
4. 参考SKILL.md中的示例代码

### Q4: 如何记录新问题和解决方案？

**A**: 
1. 打开对应skill的`TROUBLESHOOTING.md`
2. 按格式添加问题描述、原因分析、解决方案
3. 提交到git（如果解决方案验证成功）

## 📝 Skill最佳实践

### 1. 使用前先看文档
每个skill都有详细的使用说明，先阅读再使用。

### 2. 测试先行
先用小数据测试，确认成功后再批量执行。

### 3. 记录问题
遇到问题时记录到`TROUBLESHOOTING.md`，方便后续查阅。

### 4. 代码复用
优先使用已有的skill，避免重复造轮子。

### 5. 持续改进
发现skill可以优化时，及时更新代码和文档。

## 📚 相关资源

- **飞书开放平台**: https://open.feishu.cn/document/
- **SDET平台**: https://sdet.ruishan.cc/
- **项目结构说明**: `PROJECT_STRUCTURE.md`

---

**最后更新**: 2026-03-18

---

## 🤖 Skills 自动化工具

### 工具文件说明

- **skills-discovery.py**: Skills 发现和索引工具
  - 自动扫描 skills/ 目录
  - 索引所有可用技能
  - 提供搜索功能
  - 生成 skills-registry.json

- **skills-assistant.py**: Skills 智能推荐助手
  - 分析用户需求
  - 智能推荐合适的 skills
  - 提供使用指导
  - 生成推荐报告

- **skills-registry.json**: Skills 注册表
  - 存储所有 skills 的元数据
  - 自动生成,手动维护
  - 用于快速查询和推荐

### 快速开始

```bash
# 1. 更新注册表(首次使用或新增skill后)
python skills/skills-discovery.py

# 2. 使用智能推荐
python skills/skills-assistant.py
```

### 技术架构

```
skills/
├── skills-discovery.py      # 发现工具: 扫描和索引
├── skills-assistant.py      # 推荐助手: 智能推荐
├── skills-registry.json     # 注册表: 元数据存储
├── lark-skills/            # 飞书技能
├── sdet-skills/            # SDET平台技能
└── case-skills/            # 用例处理技能
```

### 工作流程

1. **扫描阶段**: `SkillsDiscovery` 扫描所有 SKILL.md 文件
2. **索引阶段**: 解析文档,提取元数据,生成注册表
3. **搜索阶段**: 根据关键词搜索相关 skills
4. **推荐阶段**: `SkillsAssistant` 分析需求,智能推荐
5. **使用阶段**: 提供使用指导和代码示例
