# 项目结构说明

本文档用于说明仓库的目录结构、各目录职责和文件放置边界。

- 如果你想了解“项目是做什么的、怎么使用、SOP 是什么”，请优先看 README.md
- 如果你想了解“Agent 的运行规则、限制和执行约束”，请看 SYSTEM_PROMPT.md
- 如果你想判断“某类脚本/模块应该放在哪个目录”，请看本文档

## 📁 目录结构

```
caseHelper/
├── scripts/               # 可执行脚本
│   ├── create/           # 创建类脚本
│   │   ├── create_directories_and_cases.py
│   │   └── create_w9qybu_cases.py
│   ├── update/           # 更新类脚本
│   │   └── update_case_names.py
│   ├── sync/             # 同步类脚本
│   │   ├── sync_directory_cases.py
│   │   ├── sync_knowledge_from_platform.py
│   │   ├── write_case_ids_to_lark.py
│   │   └── write_new_cases_to_lark.py
│   ├── analyze/          # 分析类脚本
│   │   ├── analyze_dot1x_passwd_cases.py
│   │   ├── analyze_peap_cases.py
│   │   ├── analyze_w9qybu_cases.py
│   │   ├── analyze_zwoay7_cases.py
│   │   ├── write_dot1x_to_lark.py
│   │   ├── write_peap_to_lark.py
│   │   ├── write_w9qybu_to_lark.py
│   │   └── write_zwoay7_to_lark.py
│   └── README.md         # 脚本使用指南
│
├── knowledge/            # ⭐ 轻量级知识库 (标准数据仓库)
│   ├── README.md         # 知识库说明与规范
│   ├── common_cases_manifest.json  # 核心ID映射
│   ├── case_design/      # 用例设计知识沉淀
│   │   └── insight.md    # 复盘教训与标准流程
│   └── common_cases/     # 公共用例 JSON (100+)
│
├── skills/               # 可复用能力模块
│   ├── README.md         # 能力总索引
│   ├── lark-skills/      # 飞书能力
│   │   ├── lark-access-token/    # 获取飞书 Token
│   │   ├── lark-api-helper/      # 飞书 API 综合助手
│   │   ├── lark-sheets/          # 表格结构查询
│   │   ├── lark-sheet-reader/    # 表格内容读取
│   │   └── lark-sheet-writer/    # 表格内容写入
│   ├── sdet-skills/      # SDET 平台能力
│   │   ├── platform-client/      # 平台 API 封装 (核心)
│   │   ├── batch-case-creator/   # 批量创建用例
│   │   ├── case-debugger/        # 用例审计与偏差修复
│   │   ├── case-id-backfiller/   # 用例 ID 回写飞书
│   │   └── sdet-login/           # 平台登录认证
│   └── case-skills/      # 用例分析能力
│       └── case-ai-overview/     # AI 用例概述生成
│
├── agent_service/        # Agent 代码沙箱服务 (FastAPI)
├── sandbox/              # 临时工作区（.gitignore 排除）
├── utils/                # 项目通用工具
├── archive/              # 历史归档
│
├── config.py             # 全局配置（Token、URL、知识库路径）
├── PROJECT_STRUCTURE.md  # 本文档
├── SYSTEM_PROMPT.md      # 系统提示
└── .codebuddy/
    └── rules/
        └── 项目目录规范.md
```

## 🎯 核心目录说明

### 1. **scripts/** - 可执行脚本
存放可直接运行的脚本，用于批量操作、自动化任务、验证和同步。

**子目录**：
- `create/` - 创建类脚本
- `update/` - 更新类脚本
- `sync/` - 同步类脚本
- `verify/` - 契约验证与审计脚本

**放置原则**：
- 入口脚本放在这里
- 可以依赖 `skills/` 和 `utils/`
- 不把可复用业务逻辑长期堆在这里，公共逻辑应下沉到 `skills/` 或 `utils/`

**示例**：
```bash
# 平台契约冒烟验证
python scripts/verify/contract_smoke.py

# 运行规则化审计
python scripts/verify/run_case_debugger_audit.py

# 同步公共用例知识库
python scripts/sync/sync_knowledge_from_platform.py
```

---

### 2. **skills/** - 可复用能力模块
存放可复用能力模块，是项目的主要业务能力层。

**能力清单**：
- **飞书表格读取** (`lark-skills/lark-sheet-reader/`)
- **飞书表格写入** (`lark-skills/lark-sheet-writer/`)
- **SDET 平台客户端** (`sdet-skills/platform-client/`)
- **批量建用例** (`sdet-skills/batch-case-creator/`)
- **用例审计与偏差修复** (`sdet-skills/case-debugger/`)
- **AI 用例概述** (`case-skills/case-ai-overview/`)

**放置原则**：
- 可被多个脚本复用的能力放这里
- 每个能力目录应尽量包含 `SKILL.md`
- 不把一次性临时脚本放进 `skills/`

**示例**：
```python
from platform_client import PlatformClient
```

---

### 3. **knowledge/** - 知识库与规则资产
存放公共步骤、本地同步结果、设计沉淀和审计规则。

**放置原则**：
- 需要长期维护、可审阅、可版本化的知识资产放这里
- 公共步骤 JSON、规则文件、设计复盘放这里
- 运行期临时产物不要放这里

**典型内容**：
- `common_cases/` - 公共步骤知识库
- `common_cases_manifest.json` - 别名到平台 case_id 的映射
- `case_design/` - 设计复盘与方法论
- `audit/` - 审计规则配置

---

### 4. **sandbox/** - 临时工作区
存放临时数据、测试文件、中间结果和报告产物。

**放置原则**：
- 可丢弃的运行产物放这里
- 调试中间结果、测试输出、临时报表放这里
- 不把正式知识资产或长期维护文档放这里

**注意**：
- ❌ 默认不提交新产物（由 `.gitignore` 控制）
- ✅ 定期清理临时文件

---

### 5. **根路径** - 核心配置和文档
只存放项目级别的配置文件和顶层文档。

**文件清单**：
- `config.py` - 配置文件
- `README.md` - 项目说明
- `PROJECT_STRUCTURE.md` - 结构边界文档
- `SYSTEM_PROMPT.md` - Agent 运行规则

**放置原则**：
- 根目录避免堆放一次性脚本
- 根目录避免存放大量业务数据文件
- 只有“全项目级别”的入口文件才放这里

---

## 🔄 目录规范

详细规则可参考：`.codebuddy/rules/项目目录规范.md`

**核心规则**：
1. `scripts/` 放可执行入口
2. `skills/` 放可复用能力
3. `knowledge/` 放长期维护的知识资产与规则
4. `sandbox/` 放临时产物
5. 根目录只保留全局配置与顶层文档

---

## 📌 使用建议

- 新增一个可直接运行的批处理入口：优先放 `scripts/`
- 新增一个会被多个脚本复用的能力：优先放 `skills/`
- 新增一个公共步骤/规则/设计沉淀：优先放 `knowledge/`
- 新增一个调试结果、运行报告、临时 JSON：优先放 `sandbox/`

---

**最后更新**: 2026-03-11
