# 🎯 Case Design Analyzer - 集成总结

## 📍 Skill位置

```
skills/case-skills/case-design-analyzer/
├── SKILL.md                    # 完整功能规范文档
├── README.md                   # 快速使用指南
├── case_design_analyzer.py     # 核心实现脚本
└── __init__.py                 # (可选) Python包初始化
```

## 🚀 快速开始（3步）

### Step 1: 准备输入数据
将手工用例JSON文件放到固定目录：
```
workspace/analysis/manual_cases.json
```

文件格式：
```json
[
  {
    "case_id": "TC_001",
    "case_title": "用例标题",
    "precondition": "前置条件描述",
    "steps": [
      {"step_id": 1, "description": "步骤1"},
      {"step_id": 2, "description": "步骤2"}
    ],
    "expected_result": "预期结果"
  }
]
```

💡 **示例**: 已在 `workspace/analysis/manual_cases.json` 放置了10条网络认证用例

### Step 2: 运行分析
```bash
cd d:\Code\caseHelper
python skills/case-skills/case-design-analyzer/case_design_analyzer.py
```

### Step 3: 查看报告
报告自动生成到 `workspace/analysis/case_design_reports/` 目录：

| 报告 | 格式 | 用途 |
|------|------|------|
| `20260311_HHMMSS_case_design_analysis.md` | Markdown | 完整分析报告 |
| `case_design_analysis.json` | JSON | 结构化数据 |
| `dimension_matrix.csv` | CSV | 维度组合矩阵（Excel） |
| `reusable_steps_catalog.json` | JSON | 可复用步骤目录 |

---

## 📊 分析能力清单

### 1️⃣ 前置状态机分析
识别手工用例中的**独立维度**及其值域：

**示例输出**（从10条网络认证用例识别）：
- 网络类型：wifi / 有线
- 认证方式：OPEN / WPA2 / DOT1X
- 用户身份：admin / guest
- 设备状态：未连接 / 连接中 / 已连接 / 已认证
- 密码复杂度：简单 / 复杂

### 2️⃣ 测试数据注入特征分析
识别数据源点和参数化规律：

**示例输出**：
- SSID 字段（6次）
- 密码字段（5次）
- → **推荐参数化**: `${SSID}` 和 `${password}`

### 3️⃣ 测试步骤类型分析
找出可复用步骤及其复用度：

**示例输出**（优先级排序）：
1. "打开WiFi设置页面" - 复用8次 ⭐⭐⭐
2. "点击连接" - 复用4次 ⭐⭐
3. "点击连接按钮" - 复用3次 ⭐

### 4️⃣ 验证点与状态对应分析
识别验证点的分类和对应状态：

**示例输出**：
- 验证"连接状态显示为已连接" → 对应状态 "已连接"
- 验证"显示连接失败提示" → 对应状态 "连接失败"

### 5️⃣ 自动化设计推荐输出
- **变量命名约定**：`setup_auth_type` / `setup_user_role` / `verify_connection_ok`
- **前置步骤设计**：建议的步骤标题风格和参数化方案
- **验证步骤模板**：`验证-[属性]-[预期值]`
- **实施路线图**：按优先级排序的公共步骤建设计划

---

## 🔗 与Phase 0 SOP的集成

该Skill是Phase 0"参数理解"阶段的**核心工具**：

```
📋 用户输入手工用例
    ↓
🤖 case-design-analyzer 自动分析
    ↓
📊 输出维度矩阵 + 变量方案
    ↓
✅ 用户人工审批（Phase 0.5）
    ↓
⚙️ 按照分析结果设计自动化用例
```

### Phase 0 工作流中的角色：

| Phase | 步骤 | 工具 |
|-------|------|------|
| Phase 0 | 参数理解 | **case-design-analyzer** ← 自动生成状态矩阵 |
| Phase 0.5 | 人工审批 | 用户审核报告中的维度矩阵和建议 |
| Phase 1 | 单条API验证 | platform-client |
| Phase 2 | 样本创建+审计 | batch-case-creator + case-debugger |
| Phase 3 | 批量创建 | batch-case-creator |

---

## 📈 测试验证

### 已验证功能
✅ 成功加载10条样本用例  
✅ 识别出5个维度  
✅ 发现6个可复用步骤  
✅ 识别出10个验证点  
✅ 生成4个格式的报告（MD、JSON、CSV、JSON目录）  

### 示例分析结果
```
📊 分析结果概览
✅ 用例总数: 10
✅ 识别维度: 5 个
✅ 数据源点: 2 个  
✅ 可复用步骤: 6 个
✅ 验证点: 10 个
```

---

## 💡 使用建议

### 最佳实践
1. 确保输入用例的**结构化程度高**（清晰的前置、步骤、预期结果）
2. 使用**统一的语言和术语**（避免同一概念多种表述）
3. 在**前置条件**中明确关键维度（如认证方式、用户身份）
4. 在**预期结果**中详细描述所有验证点

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 维度识别不准 | 用例描述中关键词不清晰 | 在输入用例中明确写出维度名称 |
| 步骤复用度低 | 同类步骤描述不统一 | 统一步骤描述语言 |
| 无法参数化 | 数据变化规律不明显 | 在多个用例中明确标注变化的参数 |

---

## 🔄 扩展方向

当前实现是v1，可扩展方向：

- [ ] **LLM集成**：用Claude/GPT进行更精细的语义分析和聚类
- [ ] **飞书直联**：直接从飞书表格读取手工用例
- [ ] **可视化**：生成Mermaid状态机图、维度矩阵热力图
- [ ] **交互式调整**：用户手工调整维度后重新计算
- [ ] **批量导入**：支持多个用例集合的并行分析

---

## 📚 相关文档

- 完整规范：[skills/case-skills/case-design-analyzer/SKILL.md](../../skills/case-skills/case-design-analyzer/SKILL.md)
- 快速指南：[skills/case-skills/case-design-analyzer/README.md](../../skills/case-skills/case-design-analyzer/README.md)
- Phase 0 SOP：[SYSTEM_PROMPT.md](../../SYSTEM_PROMPT.md#强制前置执行规则自动化用例生成-sop-phase-0-阻断机制)
- 示例用例：[workspace/analysis/manual_cases.json](../../workspace/analysis/manual_cases.json)

---

## 🎓 演示

已在 `workspace/analysis/` 放置了一个完整的演示：

1. **输入**：`manual_cases.json` - 10条网络认证手工用例
2. **运行**：`python skills/case-skills/case-design-analyzer/case_design_analyzer.py`
3. **输出**：4个报告文件在 `workspace/analysis/case_design_reports/`

查看生成的 Markdown 报告，了解分析的完整输出格式。

---

**Created**: 2026-03-11  
**Status**: ✅ Production Ready  
**Integration**: Phase 0 SOP核心工具
