# 用例调试器 (Case Debugger)

自动化用例质量审计与偏差修复技能。输入**业务用例目录**和**公共用例目录**，自动完成：状态机分析、偏差检测、公共用例补充、业务用例修复。

---

## 功能概览

| 阶段 | 能力 | 说明 |
|------|------|------|
| Phase 1 | **采集** | 拉取业务用例目录下所有用例及其引用步骤、变量 |
| Phase 2 | **解析** | 提取每条业务用例的"状态机"：配置组合 → 认证动作 → 期望结果 |
| Phase 3 | **对标** | 与手工用例描述比对，识别步骤缺失、顺序错误、变量遗漏 |
| Phase 4 | **诊断** | 枚举公共用例库，确认哪些公共用例已有、哪些需要新增 |
| Phase 5 | **修复** | 创建缺失公共用例 → 更新业务用例引用 → 注入变量 |

---

## 使用场景

### 场景 1：审计现有批量用例
> "我在目录 67136 下创建了 66 条 dot1x 密码复杂度的业务用例，公共用例在 66880 目录下，帮我审计一下步骤是否正确。"

### 场景 2：补充缺失的公共用例
> "分析出来有 8 种配置组合，但公共用例只有 4 条，帮我补全剩下的。"

### 场景 3：修复偏差用例
> "TP-019 的步骤缺少了'修改密码安全管理配置'这步，帮我修复。"

---

## 核心概念

### 状态机模型

每条 E2E 业务用例的步骤序列构成一条"状态机路径"：

```
[初始状态] → 配置部署 → 开户 → 认证动作 → 结果校验 → 数据清理
```

具体到 dot1x 密码复杂度场景：

```
1. 【配置】修改密码安全管理配置 (设定开关组合)
2. 【开户】指定用户名和密码开户 (创建符合/不符合策略的账户)
3. 【认证】有线1X认证 (触发认证流程)
4. 【校验】检查认证结果 (成功/失败/强制修改)
5. 【清理】删除用户/恢复配置 (可选)
```

### 偏差类型

| 偏差类型 | 定义 | 示例 |
|---------|------|------|
| **步骤缺失** | 状态机路径中缺少必要步骤 | 缺少"修改密码配置"步骤 |
| **步骤多余** | 包含不属于该状态路径的步骤 | 多了一个无关的查询步骤 |
| **顺序错误** | 步骤存在但顺序不对 | 先认证再配置（应先配置再认证） |
| **变量遗漏** | 引用的公共用例需要变量但未注入 | 引用了开户步骤但没提供username |
| **公共用例缺失** | 需要的公共步骤在平台上不存在 | 需要"全关闭模式配置"但没有 |
| **引用ID错误** | quoteId 指向了错误的公共用例 | 应引用"认证失败"但引用了"认证成功" |

---

## 工作流详解

### Phase 1: 采集数据

```python
from case_debugger import CaseDebugger

debugger = CaseDebugger(
    business_dir_id=67136,      # 业务用例目录ID
    common_dir_id=66880,        # 公共用例目录ID
)

# 1.1 拉取业务用例目录下所有子用例
business_cases = debugger.fetch_business_cases()
# 返回: [
#   {"id": 66920, "name": "【TP-019】...", "steps": [...], "variables": [...]}
#   ...
# ]

# 1.2 拉取公共用例目录下所有公共用例
common_cases = debugger.fetch_common_cases()
# 返回: [
#   {"id": 66882, "name": "【公共】修改密码配置", "inputs": [...], "outputs": [...]}
#   ...
# ]

# 1.3 加载知识库 manifest 用于交叉比对
manifest = debugger.load_manifest()
```

### Phase 2: 解析状态机

```python
# 2.1 对每条业务用例，解析其步骤引用链
analysis = debugger.analyze_cases()
# 返回: [
#   {
#     "case_id": 66920,
#     "case_name": "【TP-019】首次登录+不符合密码策略+...",
#     "state_machine": [
#       {"order": 1, "type": "quote", "quote_id": 66882, "quote_name": "修改密码配置", "category": "配置"},
#       {"order": 2, "type": "quote", "quote_id": 51400, "quote_name": "开户", "category": "开户"},
#       {"order": 3, "type": "quote", "quote_id": 66904, "quote_name": "有线1x认证失败", "category": "认证"},
#     ],
#     "variables": {"eap_username": "test", "enableCheckUserPass": "1", ...},
#     "expected_config": {
#       "首次登录强制修改": "关闭",
#       "强度检测强制处理": "开启",
#       "定时强制修改": "开启",
#       "提前短信通知": "开启"
#     }
#   }
# ]
```

### Phase 3: 偏差检测

```python
# 3.1 对比期望状态机 vs 实际步骤
deviations = debugger.detect_deviations(analysis)
# 返回: [
#   {
#     "case_id": 66920,
#     "case_name": "【TP-019】...",
#     "issues": [
#       {"type": "STEP_MISSING", "detail": "缺少'修改密码安全管理配置'步骤", "severity": "HIGH"},
#       {"type": "VAR_MISSING", "detail": "变量 enableCheckUserPass 未注入", "severity": "HIGH"},
#       {"type": "COMMON_MISSING", "detail": "需要'全关闭模式配置'公共用例但不存在", "severity": "MEDIUM"}
#     ]
#   }
# ]
```

### Phase 4: 生成修复方案

```python
# 4.1 汇总诊断报告
report = debugger.generate_report(deviations)

# 4.2 输出内容：
# - 统计概览：xx条用例有偏差，xx条正常
# - 公共用例缺口清单：需要新增哪些公共用例
# - 逐条修复建议：每条偏差用例需要做什么
# - 变量注入清单：哪些变量需要补充
```

### Phase 5: 执行修复（需用户确认）

```python
# 5.1 创建缺失的公共用例（用户确认后）
new_common_cases = debugger.create_missing_commons(report)

# 5.2 修复业务用例（补步骤/补变量/调顺序）
fix_results = debugger.fix_business_cases(report)

# 5.3 更新知识库 manifest
debugger.update_manifest(new_common_cases)
```

---

## 配置说明

### 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `business_dir_id` | int | ✅ | 业务用例所在目录ID |
| `common_dir_id` | int | ✅ | 公共用例所在目录ID |
| `manifest_path` | str | 选填 | manifest.json路径（默认读Config） |
| `dry_run` | bool | 选填 | 仅分析不修改（默认True） |

### 状态机模板

可以自定义"期望的步骤模板"来定义正确的状态机路径：

```python
# 定义 dot1x 密码复杂度场景的期望状态机
template = {
    "name": "dot1x_password_complexity",
    "expected_phases": [
        {"phase": "配置", "required": True, "common_pattern": "密码安全管理配置|密码复杂度配置"},
        {"phase": "开户", "required": True, "common_pattern": "开户|创建用户"},
        {"phase": "认证", "required": True, "common_pattern": "1[Xx]认证|EAP.*认证|dot1x"},
        {"phase": "校验", "required": False, "common_pattern": "查询|检查|校验"},
        {"phase": "清理", "required": False, "common_pattern": "删除|销户|恢复"}
    ]
}

debugger = CaseDebugger(
    business_dir_id=67136,
    common_dir_id=66880,
    state_template=template
)
```

---

## 输出格式

### 诊断报告 (Markdown)

```markdown
# 用例调试报告

## 概览
- 业务用例总数: 66
- 正常用例: 52
- 偏差用例: 14
- 公共用例缺口: 4

## 公共用例缺口
| 编号 | 建议名称 | 配置组合 | 引用场景 |
|------|---------|---------|---------|
| 1 | 【公共配置】全关闭模式 | 全关 | TP-001, TP-005 |
| 2 | 【公共配置】仅定时修改 | 首次=关,强度=关,定时=开 | TP-010 |

## 偏差用例明细
### TP-019 (ID: 66920)
- ❌ STEP_MISSING: 缺少"修改密码安全管理配置"步骤 [HIGH]
- ❌ VAR_MISSING: 变量 enableCheckUserPass 未注入 [HIGH]
- 🔧 修复方案: 在 order=1 处插入引用步骤 quoteId=66882，注入10个配置变量
```

---

## 安全约束

- ✅ **Phase 1-4 纯只读**：采集和分析阶段不修改任何平台数据
- ✅ **Phase 5 需确认**：修复操作必须用户确认后才执行
- ✅ **dry_run 默认开启**：首次运行只生成报告
- ✅ **只增不删**：修复只添加步骤/变量，不删除已有内容
- ✅ **操作可回溯**：每次修复记录到 `sandbox/workspace/debug_fix_log_<timestamp>.json`

---

## 依赖说明

```
case-debugger/
├── 依赖: skills/sdet-skills/platform-client/    → PlatformClient (API交互)
├── 依赖: knowledge/common_cases_manifest.json    → 公共用例索引
├── 依赖: knowledge/common_cases/*.json           → 公共用例详情
└── 依赖: config.py                               → 平台配置
```

---

## 典型使用示例

### 完整审计流程

```python
import sys
sys.path.insert(0, 'skills/sdet-skills/case-debugger')
from case_debugger import CaseDebugger

# 初始化（默认 dry_run=True）
debugger = CaseDebugger(
    business_dir_id=67136,    # dot1x密码复杂度业务用例
    common_dir_id=66880       # dot1x公共用例
)

# 全流程执行
report = debugger.run_full_audit()

# 查看报告
print(report.to_markdown())

# 确认后执行修复
debugger.dry_run = False
fix_result = debugger.execute_fixes(report)
print(f"修复完成: {fix_result['fixed_count']} 条用例已更新")
```

---

## 版本说明

当前版本：v1.0
- 初始版本，支持 E2E 引用式用例的状态机分析
- 支持公共用例缺口检测
- 支持偏差修复（补步骤/补变量）
- 生成 Markdown 诊断报告
