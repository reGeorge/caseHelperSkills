# case-design-analyzer - 用例设计分析工具

## 快速开始

### 1. 准备输入数据

在 `workspace/analysis/` 创建 `manual_cases.json` 文件，格式如下：

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
  {
    "case_id": "TC_002",
    "case_title": "验证WPA2密码错误",
    "precondition": "WiFi已配置为WPA2认证方式（SSID: Test_WPA2，密码: Correct123）",
    "steps": [
      {"step_id": 1, "description": "进入WiFi设置页面"},
      {"step_id": 2, "description": "选择'Test_WPA2'网络"},
      {"step_id": 3, "description": "输入错误密码：WrongPassword"},
      {"step_id": 4, "description": "点击连接"}
    ],
    "expected_result": "显示连接失败提示，连接状态显示为未连接"
  }
]
```

### 2. 运行分析

```bash
cd skills/case-skills/case-design-analyzer
python case_design_analyzer.py
```

### 3. 查看结果

报告输出到 `workspace/analysis/case_design_reports/` 目录：

- **20260311_HHMMSS_case_design_analysis.md** - 完整分析报告（Markdown格式）
- **case_design_analysis.json** - 结构化分析数据
- **dimension_matrix.csv** - 维度组合矩阵
- **reusable_steps_catalog.json** - 可复用步骤目录

---

## 输出报告说明

### 主报告（Markdown）

包含：
1. **前置状态机分析** - 识别的维度、值域、状态转移规律
2. **测试数据注入特征** - 数据源点、参数化维度、等价类划分
3. **测试步骤类型分析** - 步骤种类分布、可复用步骤清单
4. **验证点与状态对应** - 验证点分类、验证-状态矩阵
5. **自动化设计推荐** - 前置步骤设计、变量命名、验证步骤设计
6. **实施路线图** - 公共步骤优先级排序

### 维度矩阵（CSV）

Excel友好格式，列出所有维度及建议操作：

```
D1,网络认证方式,枚举,OPEN,WPA2,DOT1X,,,需补充
D2,用户身份,枚举,admin,guest,,,需补充
```

### 可复用步骤目录（JSON）

按类型分类的步骤清单，包含复用度和优先级：

```json
{
  "setup_steps": [
    {
      "step_id": "STEP_001",
      "title": "进入WiFi设置页面",
      "reuse_count": 8,
      "priority": "HIGH"
    }
  ]
}
```

---

## 与Phase 0 SOP的集成

该工具输出的**维度组合矩阵**正是 Phase 0 所需的"状态矩阵分析"结果：

1. **Phase 0（参数理解）**
   - 用户输入手工用例
   - 运行 `case-design-analyzer` 获得维度矩阵
   - 系统向用户展示并请求审批

2. **Phase 0.5（人工审批）**
   - 用户核对维度是否遗漏
   - 用户确认每个维度值对应的API特征

3. **Phase 1+（批量创建）**
   - 按审批后的矩阵构建公共步骤
   - 使用变量方案进行参数化
   - 批量创建自动化用例

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| "输入文件不存在" | 缺少manual_cases.json | 在workspace/analysis/目录创建文件 |
| "维度识别不准确" | 用例描述不结构化 | 标准化描述格式，确保关键信息清晰 |
| "报告生成失败" | 输出目录权限问题 | 检查workspace/analysis/case_design_reports/目录权限 |
| "步骤识别度低" | 同类步骤描述不统一 | 在源用例中统一步骤描述语言 |

---

## 使用建议

1. **最佳实践**：
   - 确保输入用例数据的一致性和完整性
   - 在前置条件和预期结果中明确关键维度和状态
   - 使用统一的步骤描述语言（避免同种操作的多种表述）

2. **迭代优化**：
   - 第一次运行后查看识别结果
   - 根据反馈调整输入数据格式
   - 重新运行获得更精准的分析结果

3. **与其他工具的组合**：
   - `lark-sheet-reader` → 从飞书读取手工用例
   - `batch-case-creator` → 使用分析结果创建自动化用例
   - `case-debugger` → 用分析结果验证自动化用例的完整性

---

## 扩展方向

- 集成LLM（Claude/GPT）用于更精细的语义分析
- 支持从飞书表格直接读取用例
- 生成Mermaid状态机图表
- 支持交互式维度调整和结果微调
