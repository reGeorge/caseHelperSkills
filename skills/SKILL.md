---
name: casehelper-skills
description: This skill provides comprehensive capabilities for test case management, including Feishu spreadsheet integration, SDET platform operations, automated test case creation, case debugging and analysis. Use this skill when users need to read/write Feishu sheets, interact with the SDET test automation platform, batch create test cases, or perform case quality audits and deviation fixes.
allowed-tools: [read_file, write_to_file, replace_in_file, search_content, search_file, list_dir, execute_command, web_search, web_fetch, task]
disable: false
---

# CaseHelper Skills 综合能力库

CaseHelper Skills 是一个专业的测试用例管理自动化能力库，封装了飞书表格操作、SDET自动化测试平台交互、批量用例创建、用例调试与分析等核心能力。

## 📚 能力总览

### 1. 飞书表格能力 (lark-skills)
- **lark-access-token**: 获取飞书应用访问令牌
- **lark-sheet-reader**: 读取飞书表格内容并转换为 JSON
- **lark-sheet-writer**: 向飞书表格写入或更新数据
- **lark-sheets**: 获取表格的所有工作表信息
- **lark-api-helper**: 飞书API综合辅助工具

### 2. SDET平台能力 (sdet-skills)
- **platform-client**: SDET平台API客户端封装（核心模块）
- **sdet-login**: 平台登录认证，处理401鉴权失效
- **batch-case-creator**: 从飞书表格批量创建测试用例
- **case-debugger**: 用例质量审计与偏差修复
- **case-id-backfiller**: 用例ID回写到飞书表格

### 3. 用例分析能力 (case-skills)
- **case-ai-overview**: 使用AI生成测试用例概述
- **case-design-analyzer**: 测试用例设计模式分析器
- **script-name-generator**: 自动化用例脚本名称生成器
- **test-case-analyzer**: 测试用例分析工具

## 🎯 使用场景

### 场景1: 批量创建测试用例
当用户需要从飞书表格批量创建测试用例到SDET平台时：
1. 使用 `lark-sheet-reader` 读取飞书表格数据
2. 使用 `batch-case-creator` 批量创建用例
3. 使用 `case-id-backfiller` 将用例ID回写到飞书表格

### 场景2: 用例质量审计
当用户需要审计已创建的自动化用例质量时：
1. 使用 `case-debugger` 分析用例状态机和偏差
2. 使用 `case-design-analyzer` 深度分析设计模式
3. 使用 `platform-client` 获取用例详情和步骤信息

### 场景3: 飞书表格数据同步
当用户需要在飞书表格和SDET平台之间同步数据时：
1. 使用 `lark-sheets` 获取表格结构
2. 使用 `lark-sheet-reader` 读取数据
3. 使用 `lark-sheet-writer` 写入或更新数据

### 场景4: API鉴权处理
当用户遇到SDET平台401错误或需要重新登录时：
1. 使用 `sdet-login` 通过账号密码重新登录
2. 自动保存新的token到配置文件

## 🚀 快速开始

### 读取飞书表格
```python
import sys
sys.path.insert(0, 'skills/lark-skills/lark-sheet-reader')
from lark_sheet_reader import LarkSheetReader

reader = LarkSheetReader(app_id, app_secret)
data = reader.read_from_url('https://ruijie.feishu.cn/sheets/xxx?sheet=xxx')
```

### 操作SDET平台
```python
import sys
sys.path.insert(0, 'skills/sdet-skills/platform-client')
from platform_client import PlatformClient

client = PlatformClient(base_url, token)
case_detail = client.get_case(case_id)
```

### 用例审计
```python
import sys
sys.path.insert(0, 'skills/sdet-skills/case-debugger')
from case_debugger import CaseDebugger

debugger = CaseDebugger(business_dir_id, common_dir_id)
report = debugger.run_full_audit()
```

## 📖 文档位置

每个技能都有独立的 SKILL.md 文档，位于对应的 skill 目录下：
- `skills/lark-skills/<skill-name>/SKILL.md`
- `skills/sdet-skills/<skill-name>/SKILL.md`
- `skills/case-skills/<skill-name>/SKILL.md`

## 🔧 技术依赖

- Python 3.7+
- requests: HTTP请求
- 飞书开放平台API
- SDET自动化测试平台API

## ⚠️ 重要提示

1. **凭证管理**: 所有鉴权Token已注入环境变量，请通过 `os.getenv()` 读取
2. **文件隔离**: 所有临时文件读写操作必须在当前工作目录进行
3. **安全约束**: 只新增不删除，确保数据安全
4. **文档先行**: 使用技能前请先阅读对应 skill 的 SKILL.md 文档

## 🔄 工作流程

### 批量建用例标准流程
1. **Phase 0**: 分析飞书表格，生成状态矩阵和维度分析
2. **Phase 1**: 确认API契约，创建公共步骤和目录
3. **Phase 2**: 批量创建业务用例
4. **Phase 3**: 将用例ID回写到飞书表格

详细流程请参考: `knowledge/SOP_批量建用例.md`

## 📚 相关资源

- **项目结构说明**: `PROJECT_STRUCTURE.md`
- **系统提示**: `SYSTEM_PROMPT.md`
- **SOP文档**: `knowledge/SOP_批量建用例.md`
- **技能发现系统**: `skills/skills-discovery.py`
- **智能推荐**: `skills/skills-assistant.py`
