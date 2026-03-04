# 项目结构说明

## 📁 目录结构

```
caseHelper/
├── agent_service/          # Agent服务模块
│   ├── main.py
│   ├── security.py
│   ├── agent_service.py
│   ├── requirements.txt
│   └── agent_config.yaml
│
├── skills/                 # 核心能力库
│   ├── lark-skills/       # 飞书能力
│   │   ├── lark-sheet-reader/    # 表格读取
│   │   └── lark-sheet-writer/    # 表格写入
│   │       ├── SKILL.md
│   │       └── TROUBLESHOOTING.md
│   │
│   ├── sdet-skills/       # SDET平台能力
│   │   ├── sdet-api-helper/      # API辅助
│   │   │   ├── sdet-api-info.md
│   │   │   └── README.md
│   │   └── batch-case-creator/   # 批量创建
│   │       └── scripts/
│   │           └── read_lark_sheet.py
│   │
│   └── case-skills/       # 用例管理能力
│       └── test-case-analyzer/   # 用例分析器
│           ├── test_case_analyzer.py
│           └── README.md
│
├── sandbox/               # 工作区（不提交git）
│   └── workspace/
│       ├── lark_latest_data.json         # 飞书最新数据
│       ├── test_case_analysis.json       # 用例分析结果
│       ├── case_id_mapping.json          # 用例ID映射
│       ├── creation_result_*.json        # 创建结果
│       ├── directory_structure_by_config.md  # 目录结构文档
│       └── test_case_analysis_report.md  # 分析报告
│
├── utils/                 # 工具函数
│   ├── logger.py
│   └── __init__.py
│
├── archive/               # 归档目录
│   └── [过期数据]
│
├── config.py              # 配置文件
├── write_case_ids_to_lark.py  # 飞书写入脚本
├── write_new_cases_to_lark.py # 飞书回写脚本
├── create_directories_and_cases.py  # 批量创建脚本
├── update_case_names.py   # 用例名称更新脚本
├── PROJECT_STRUCTURE.md   # 本文档
└── SYSTEM_PROMPT.md       # 系统提示
```

## 🎯 核心文件说明

### 主要脚本

| 文件 | 功能 | 用途 |
|------|------|------|
| `create_directories_and_cases.py` | 批量创建自动化目录和用例 | 在SDET平台创建用例结构 |
| `update_case_names.py` | 批量更新用例名称 | 修复用例名称缺失问题 |
| `write_case_ids_to_lark.py` | 回写用例ID到飞书 | 同步自动化ID到飞书表格 |
| `write_new_cases_to_lark.py` | 回写新创建用例ID | 同步新创建的用例信息 |
| `config.py` | 配置文件 | 存储平台配置信息 |

### Skills能力库

| Skill | 功能 | 文件位置 |
|-------|------|---------|
| **飞书表格读取** | 从飞书表格读取数据 | `skills/lark-skills/lark-sheet-reader/` |
| **飞书表格写入** | 写入数据到飞书表格 | `skills/lark-skills/lark-sheet-writer/` |
| **SDET API辅助** | SDET平台API封装 | `skills/sdet-skills/sdet-api-helper/` |
| **用例分析器** | 分析手工用例结构 | `skills/case-skills/test-case-analyzer/` |

### 工作区数据（sandbox/）

| 文件 | 说明 |
|------|------|
| `lark_latest_data.json` | 飞书表格最新数据（28条用例） |
| `test_case_analysis.json` | 用例结构化分析结果 |
| `case_id_mapping.json` | 手工用例ID到自动化用例ID映射 |
| `creation_result_*.json` | 批量创建结果记录 |
| `directory_structure_by_config.md` | 按配置状态分类的目录结构 |

## 📊 项目统计

| 项目 | 数量 |
|------|------|
| Skills能力 | 4个 |
| 主要脚本 | 5个 |
| 工作区数据 | 8个核心文件 |
| Git提交 | 23次 |

## 🔗 快速访问

### SDET平台
- 父目录: https://sdet.ruishan.cc/ap/atp/apiCase?parent=66469
- 用例列表: https://sdet.ruishan.cc/ap/atp/apiCase?parent=66470

### 飞书表格
- 手工用例: https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=dfa872

## 📝 使用指南

### 1. 创建自动化用例
```bash
python create_directories_and_cases.py
```

### 2. 更新用例名称
```bash
python update_case_names.py
```

### 3. 回写飞书表格
```bash
python write_new_cases_to_lark.py
```

### 4. 分析手工用例
```python
from skills.case-skills.test-case-analyzer.test_case_analyzer import TestCaseAnalyzer

analyzer = TestCaseAnalyzer()
analyzer.load_from_file('sandbox/workspace/lark_latest_data.json')
result = analyzer.analyze()
```

## 🎯 项目成果

✅ 28个手工用例100%自动化  
✅ 12个目录按配置状态分类  
✅ 飞书表格实时同步  
✅ 完整的Skills能力库  

---

**最后更新**: 2026-03-04  
**维护者**: 魏斌
