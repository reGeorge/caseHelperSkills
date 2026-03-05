# 项目结构说明

## 📁 目录结构

```
caseHelper/
├── scripts/               # 可执行脚本
│   ├── create/           # 创建类脚本
│   │   └── create_directories_and_cases.py
│   ├── update/           # 更新类脚本
│   │   └── update_case_names.py
│   ├── sync/             # 同步类脚本
│   │   ├── write_case_ids_to_lark.py
│   │   └── write_new_cases_to_lark.py
│   ├── utils/            # 工具函数
│   └── README.md         # 脚本使用指南
│
├── skills/               # 可复用能力模块
│   ├── lark-skills/      # 飞书能力
│   │   ├── lark-sheet-reader/
│   │   └── lark-sheet-writer/
│   ├── sdet-skills/      # SDET平台能力
│   │   ├── sdet-api-helper/
│   │   └── batch-case-creator/
│   └── case-skills/      # 用例管理能力
│       └── test-case-analyzer/
│
├── sandbox/              # 临时工作区（默认不提交新产物）
│   └── workspace/
│       ├── lark_latest_data.json
│       ├── test_case_analysis.json
│       ├── case_id_mapping.json
│       ├── creation_result_*.json
│       ├── directory_structure_by_config.md
│       └── test_case_analysis_report.md
│
├── agent_service/        # Agent服务模块
├── utils/                # 项目通用工具
├── archive/              # 历史归档目录（当前无快照）
│
├── config.py             # 配置文件
├── PROJECT_STRUCTURE.md  # 本文档
├── SYSTEM_PROMPT.md      # 系统提示
└── .codebuddy/
    └── rules/
        └── 项目目录规范.md
```

## 🎯 核心目录说明

### 1. **scripts/** - 可执行脚本
存放可直接运行的脚本，用于批量操作、自动化任务等

**子目录**：
- `create/` - 创建类脚本
- `update/` - 更新类脚本
- `sync/` - 同步类脚本
- `utils/` - 工具函数

**使用方法**：
```bash
# 创建目录和用例
python scripts/create/create_directories_and_cases.py

# 更新用例名称
python scripts/update/update_case_names.py

# 同步到飞书
python scripts/sync/write_case_ids_to_lark.py
```

---

### 2. **skills/** - 可复用能力模块
存放可被其他脚本调用的函数库和类

**能力清单**：
- **飞书表格读取** (`lark-skills/lark-sheet-reader/`)
- **飞书表格写入** (`lark-skills/lark-sheet-writer/`)
- **SDET API辅助** (`sdet-skills/sdet-api-helper/`)
- **用例分析器** (`case-skills/test-case-analyzer/`)

**使用方法**：
```python
from skills.case-skills.test-case-analyzer.test_case_analyzer import TestCaseAnalyzer
from skills.lark-skills.lark-sheet-writer.lark_sheet_writer import LarkSheetWriter
```

---

### 3. **sandbox/** - 临时工作区
存放临时数据、测试文件、中间结果等

**重要文件**：
- `lark_latest_data.json` - 飞书表格最新数据
- `test_case_analysis.json` - 用例分析结果
- `case_id_mapping.json` - 用例ID映射
- `creation_result_*.json` - 创建结果
- `directory_structure_by_config.md` - 目录结构文档

**注意**：
- ❌ 默认不提交新产物（由 `.gitignore` 控制）
- ✅ 定期清理临时文件

---

### 4. **根路径** - 核心配置和文档
只存放项目级别的配置文件和文档

**文件清单**：
- `config.py` - 配置文件
- `PROJECT_STRUCTURE.md` - 项目结构文档
- `SYSTEM_PROMPT.md` - 系统提示
- `README.md` - 项目说明

---

## 📊 项目统计

| 项目 | 数量 |
|------|------|
| 脚本 | 4个 |
| Skills能力 | 4个 |
| 核心数据文件 | 8个 |
| Git提交 | 25次 |

---

## 🔄 目录规范

详细的目录规范请查看：`.codebuddy/rules/项目目录规范.md`

**核心规则**：
1. **scripts/** - 可执行脚本
2. **skills/** - 可复用能力模块
3. **sandbox/** - 临时工作区
4. **根路径** - 核心配置和文档

---

## 🔗 快速访问

### SDET平台
- 父目录: https://sdet.ruishan.cc/ap/atp/apiCase?parent=66469
- 用例列表: https://sdet.ruishan.cc/ap/atp/apiCase?parent=66470

### 飞书表格
- 手工用例: https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=dfa872

---

## 🎯 项目成果

✅ 28个手工用例100%自动化  
✅ 12个目录按配置状态分类  
✅ 飞书表格实时同步  
✅ 完整的Skills能力库  
✅ 清晰的项目结构  

---

**最后更新**: 2026-03-05  
**维护者**: 魏斌
