# Case Design Analyzer - 测试用例设计分析器

> **目标**：在手工用例向自动化用例转换过程中，通过深度分析手工用例的设计模式，生成中间分析报告，指导自动化步骤的设计和参数化变量的构造。

## Overview

`case-design-analyzer` 是一个用例设计智能分析工具，帮助测试工程师快速理解手工用例的共性设计思路，并推导出自动化用例的核心要素和变量设计方案。

### 核心价值

1. **设计模式识别**：从大量手工用例中自动识别共性的前置条件模式、测试数据特征、步骤结构
2. **状态机构建**：分析用例前置条件与验证点的对应关系，构建完整的状态转移图
3. **自动化设计指导**：根据分析结果，生成可执行的自动化设计方案（变量命名、公共步骤结构、验证点映射）
4. **质量保障**：确保自动化用例不遗漏手工设计中的关键维度

---

## Core Capabilities

### 1. 手工用例设计深度分析

#### 1.1 前置条件状态机识别
- **多维度提取**：解析每条用例的前置条件，识别独立的状态维度
  - 示例：网络认证模式（OPEN / WPA2 / DOT1X）、设备状态（连接 / 已认证 / 断开）、用户身份（admin / guest）
  - 输出：维度列表 + 各维度的值域集合
  
- **互依赖关系分析**：检测维度间是否存在前后置约束
  - 示例：若认证方式为OPEN，则不需要密码维度；若网络为有线，则不支持WiFi信道维度
  - 输出：依赖矩阵（前置-后置关系）

- **状态转移规律**：识别测试步骤中的状态转移序列
  - 示例：认证前 → 发起认证 → 认证中 → 认证后 / 认证失败
  - 输出：状态转移图

#### 1.2 测试数据注入特征分析
- **数据源识别**：找出用例中的数据注入点
  - 示例：用户名字段、密码字段、SSID、证书、服务器地址
  - 分类：常量 / 变量（待参数化）

- **参数化规律识别**：识别数据参数的变化模式
  - 示例：密码长度变化 / 特殊字符测试 / 中英文混合
  - 输出：参数化维度列表

- **数据值域划分**：对参数同类值进行分组
  - 示例：密码→有效密码组、无效密码组、边界值
  - 输出：等价类划分表

#### 1.3 测试步骤种类分类
- **步骤类型识别**：将用例中的操作步骤分类
  - UI操作：点击、输入、选择、滚动
  - API调用：查询、修改、删除、创建
  - 系统验证：状态检查、日志查询、数据库查询
  - 前置准备：环境配置、数据初始化
  
- **步骤复用度分析**：识别多个用例中重复出现的步骤序列
  - 示例："进行WPA2认证"、"修改网络参数"、"验证连接状态"
  - 输出：可独立为公共步骤的步骤集合

- **步骤与状态的映射**：建立步骤执行与状态转移的对应关系
  - 示例：步骤"输入密码并点击连接" → 状态转移"认证前" → "认证中"
  - 输出：步骤-状态映射表

#### 1.4 验证点与状态机的对应分析
- **验证点提取**：从每条用例的"预期结果"中提取验证点
  - 示例：验证"连接状态显示为已连接"、"信号强度为-50dBm"
  
- **验证点分类**：按验证维度分类
  - UI验证：页面元素、显示文本
  - 状态验证：网络状态、设备属性
  - 数据验证：日志记录、数据库记录
  
- **验证点与状态的对应**：映射验证点到特定的状态机状态
  - 示例：验证"连接成功"对应状态"已连接"
  - 输出：验证点-状态矩阵

---

### 2. 自动化步骤核心要素设计

#### 2.1 前置步骤命名风格指导
输出建议的前置步骤命名规则，确保自动化用例中的共享步骤具有清晰的语义：

- **命名模板**：`[模块]+[操作]+[主体]+[关键参数]`
  - 示例：`WiFi-配置为-开放式网络` / `认证-执行-WPA2-密码验证`
  - 规则：动词为主，参数作为修饰
  
- **参数化命名方案**：
  - 常量前置步骤：`WiFi配置为开放式网络`
  - 参数化前置步骤：`WiFi配置为-{wifi_auth_type}-{wifi_password}`
  - 多参数组合：`执行认证_auth_type={auth_type}_username={username}`

- **前置步骤粒度建议**：
  - 粒度过小（单动作）→ 步骤数爆炸，不利于维护
  - 粒度过大（多个独立操作）→ 复用度低，难以组合
  - **推荐粒度**：一个完整的业务操作（如"完成WPA2认证"）

#### 2.2 数据注入变量控制方案
根据分析结果，设计变量命名和作用域：

- **变量命名约定**：
  - 前置状态变量：`setup_[dimension]` / `初始_[维度]`
    - 示例：`setup_network_auth_type`、`setup_user_role`
  - 测试数据变量：`data_[field]_[variant]` 或 `test_[category]`
    - 示例：`data_password_invalid`、`test_credential_length`
  - 验证变量：`verify_[assertion_type]` 或 `check_[field]`
    - 示例：`verify_connection_success`、`check_signal_strength`

- **变量值域定义**：为每个变量列出可能的取值
  - 示例变量：`auth_type`
    - 允许值：`OPEN / WPA2 / DOT1X / NONE`
    - 类型：枚举
    - 最大长度：N/A
  
- **变量作用域明确**：
  - 全局变量（在Suite级别定义）：环境配置、通用凭证
  - 用例级变量（在Case级别定义）：特定用例的测试数据
  - 步骤级变量（在Step级别定义）：仅在特定步骤内使用的临时值

#### 2.3 验证点对应的公共步骤设计
为每个验证点设计对应的验证步骤，确保验证逻辑可复用：

- **验证步骤模板**：`验证-[状态/属性]-[预期值/范围]`
  - 示例：`验证WiFi连接状态为已连接` / `验证信号强度在-60到-40dBm之间`

- **验证步骤的变量参数**：
  - 验证方式参数：检查UI / 查询API / 查看日志
  - 预期值参数：固定值 / 范围值 / 动态值（从其他步骤输出）
  - 超时参数：等待UI更新、异步操作完成

- **验证步骤的组织方案**：
  - 单点验证步骤：对应单一验证点（原子性）
  - 关联验证步骤：验证多个字段的一致性（如："用户登录后，用户名字段和账户信息一致"）
  - 状态转移验证：验证前后状态的变化（如："认证前状态为未连接，认证后状态为已连接"）

---

## Report Output Structure

分析报告输出位置：**`workspace/analysis/case_design_reports/`**

### 报告文件清单

#### 1. `20260311_case_design_analysis.md` （主报告）
Markdown格式，包含完整的分析结果和设计建议。

**章节结构**：
```
# 用例设计分析报告

## 执行信息
- 分析时间
- 分析源数据文件
- 用例总数 / 分析覆盖率

## 第一部分：手工用例设计模式识别

### 1. 前置状态机分析
- 识别出的维度（表格）
- 维度值域（树形结构）
- 状态转移规律（状态机图表，Mermaid格式）
- 维度依赖关系（矩阵）

### 2. 测试数据注入特征
- 数据源点统计（表格）
- 参数化维度列表（表格）
- 等价类划分方案（表格）
- 数据变化模式识别（分析文本）

### 3. 测试步骤类型分析
- 步骤类型分布（柱状图，Mermaid格式）
- 可复用步骤清单（表格）
- 步骤-状态映射（矩阵表）

### 4. 验证点与状态对应分析
- 验证点分类统计（表格）
- 验证点-状态映射矩阵
- 覆盖度分析（哪些状态缺少验证）

## 第二部分：自动化设计推荐方案

### 5. 前置步骤设计指导
- 建议的前置步骤清单（含参数化方案）
- 前置步骤命名规范示例
- 前置步骤聚合建议（步骤粒度分析）

### 6. 数据注入变量设计方案
- 推荐的变量命名约定
- 变量清单与值域定义（表格）
- 变量作用域分配（Suite / Case / Step）
- 参数化示例（以具体用例演示）

### 7. 验证步骤设计方案
- 验证步骤模板化设计
- 验证步骤清单（含参数方案）
- 验证覆盖度建议（缺失的验证点）

## 第三部分：实施路线图

### 8. 公共步骤优先级
- 优先级排序（关键性 × 复用度）
- 分阶段建设计划（第一阶段 / 第二阶段 / ）

### 9. 风险与遗漏检查清单
- 大用例中是否遗漏了某些维度组合
- 预期难以参数化的步骤标记
- 推荐的验证方式（UI / API / 日志 / 数据库）

### 10. 附录：原始数据引用
- 样本用例详细分析（2-3个代表性用例）
- 分析数据源文件路径
```

#### 2. `case_design_analysis.json` (结构化数据)
包含所有分析结果的结构化JSON，便于后续工具化处理：

```json
{
  "metadata": {
    "analysis_time": "2026-03-11T10:30:00",
    "source_file": "workspace/analysis/manual_cases.json",
    "total_cases": 42,
    "coverage_rate": 0.95
  },
  "state_machine": {
    "dimensions": [...],
    "dimension_values": {...},
    "state_transitions": {...},
    "dimension_dependencies": [...]
  },
  "test_data": {
    "data_sources": [...],
    "parameterization_dimensions": [...],
    "equivalence_classes": {...}
  },
  "steps": {
    "step_type_distribution": {...},
    "reusable_steps": [...],
    "step_state_mapping": [...]
  },
  "verification": {
    "verification_points": [...],
    "verification_classification": {...},
    "verification_state_mapping": [...]
  },
  "automation_design": {
    "setup_steps": [{
      "title_template": "...",
      "parameters": [...]
    }],
    "variables": [{
      "name": "...",
      "scope": "...",
      "type": "...",
      "allowed_values": [...]
    }],
    "verification_steps": [...]
  },
  "implementation_roadmap": [...]
}
```

#### 3. `dimension_matrix.csv` (维度组合矩阵)
Excel友好格式，列出所有识别的维度及其组合：

```
Dimension_ID,维度名称,类型,值_1,值_2,值_3,当前覆盖_已有公共步骤,建议操作
D1,网络认证方式,枚举,OPEN,WPA2,DOT1X,WPA2已有步骤,需补充OPEN和DOT1X
D2,用户身份,枚举,admin,guest,,admin有步骤,需补充guest
...
```

#### 4. `reusable_steps_catalog.json` (可复用步骤目录)
按照前置 → 操作 → 验证分类：

```json
{
  "setup_steps": [
    {
      "step_id": "SETUP_001",
      "title_template": "WiFi配置为{auth_type}",
      "variables": ["auth_type"],
      "examples": ["WiFi配置为OPEN", "WiFi配置为WPA2"],
      "reuse_count": 8,
      "priority": "HIGH"
    }
  ],
  "verification_steps": [...],
  "transition_steps": [...]
}
```

---

## Usage

### Phase 1: 准备输入数据

将需要分析的手工用例数据组织为JSON文件，放在 `workspace/analysis/` 下：

```json
[
  {
    "case_id": "TC_001",
    "case_title": "验证开放式WiFi连接成功",
    "precondition": "WiFi已经配置为开放式网络（SSID: Test_Open）",
    "steps": [
      {"step_id": 1, "description": "进入WiFi设置页面"},
      {"step_id": 2, "description": "选择'Test_Open'网络"},
      {"step_id": 3, "description": "点击连接"}
    ],
    "expected_result": "连接状态显示为已连接，信号强度正常"
  },
  ...
]
```

### Phase 2: 执行分析

```python
from case_design_analyzer import CaseDesignAnalyzer

# 初始化
analyzer = CaseDesignAnalyzer()

# 运行分析
analyzer.analyze(input_file="workspace/analysis/manual_cases.json")

# 生成报告
analyzer.generate_reports()

# 报告输出到 workspace/analysis/case_design_reports/
```

### Phase 3: 查看和应用结果

1. 打开 `workspace/analysis/case_design_reports/20260311_case_design_analysis.md` 查看完整分析
2. 参考"自动化设计推荐方案"章节设计自动化步骤
3. 使用"数据注入变量设计方案"指导参数化变量的构造
4. 根据"公共步骤优先级"建设公共步骤库

---

## Integration with Phase 0 SOP

该Skill与 `SYSTEM_PROMPT.md` 中的 Phase 0 状态矩阵分析深度集成：

| Phase | 任务 | 工具 |
|-------|------|------|
| **Phase 0** | 参数理解 + 用例理解 | `case-design-analyzer` 自动生成状态矩阵 |
| Phase 0.5 | 用户审批 | 人工审批报告中的"维度组合矩阵" |
| Phase 1 | 单条API验证 | 平台-client + 已有脚本 |
| Phase 2 | 样本创建 + 审计 | batch-case-creator + case-debugger |
| Phase 3 | 批量创建 | batch-case-creator |

---

## Dependencies

核心依赖：
- Python 3.7+
- json, re, dataclasses
- 可选：pandas（用于生成CSV报告）、jinja2（用于报告模板生成）

可选优化：
- LLM集成（Claude / GPT）：用于聊天式的字段归类和维度识别
- 可视化：matplotlib / plotly（绘制状态机图、维度矩阵热力图）

---

## Examples

### 示例：网络认证测试用例分析

**输入**：15条网络认证相关的手工用例

**输出高亮**：

1. **识别的维度**：
   - 网络类型（有线 / 无线）
   - 认证方式（OPEN / WPA / DOT1X）
   - 用户身份（admin / guest）
   - 密码复杂度（简单 / 复杂）

2. **维度依赖**：
   - 网络类型=有线 → 不支持WiFi信道维度
   - 认证方式=OPEN → 不需要密码维度

3. **可复用步骤**：
   - "执行WPA2认证"（在7个用例中复用）→ 优先级HIGH
   - "验证连接成功"（在6个用例中复用）→ 优先级HIGH

4. **变量设计**：
   - `setup_auth_type`: OPEN | WPA2 | DOT1X
   - `setup_user_role`: admin | guest
   - `verify_connection_ok`: true | false

---

## Troubleshooting

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| "分析不出来维度" | 输入用例描述不够结构化 | 确保每条用例都有明确的"前置条件、步骤、预期结果" |
| "公共步骤识别度低" | 用例中步骤描述差异大 | 标准化步骤描述语言，或手工标注"关键步骤类型" |
| "报告文件未生成" | 输出目录不存在 | 确保 `workspace/analysis/case_design_reports/` 目录存在 |

---

## Notes

- 该Skill的输出是**指导性建议**，不是最终方案。用户需审核并调整。
- 分析质量取决于输入用例的**质量和结构化程度**。
- 推荐在 Phase 0 时运行该分析，作为"用例理解"阶段的工具。
