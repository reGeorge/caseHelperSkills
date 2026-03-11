# caseHelper - SDET 自动化用例管理工具

本文档是项目主说明文档，用于说明项目目标、核心能力、SOP、验证方式和使用入口。

面向 SDET 团队的端到端用例管理工具，覆盖：

- 飞书手工用例读取
- 平台公共步骤与自动化用例批量创建
- 审计与偏差修复
- 平台与本地知识库同步

---

## 项目定位

本项目的目标是把“手工用例 -> 自动化用例”的链路标准化，并通过 SOP 减少批量创建时的漏项和返工。

重点解决：

- 手工用例与平台自动化用例数据分散
- 批量建用例时状态组合遗漏
- 公共步骤复用不稳定、更新后难追踪
- 批量创建后的质量审计与回写闭环不足

---

## 核心能力

### 飞书能力（skills/lark-skills）

- `lark-access-token`：获取飞书访问令牌
- `lark-sheets`：读取表格元信息
- `lark-sheet-reader`：读取手工用例并转结构化 JSON
- `lark-sheet-writer`：将结果写回飞书

### 平台能力（skills/sdet-skills）

- `platform-client`：目录/用例/步骤/变量 API 封装
- `batch-case-creator`：批量创建自动化用例
- `case-debugger`：偏差检测与修复建议
- `case-id-backfiller`：平台 case_id 回写飞书

### 知识与分析能力

- `knowledge/common_cases`：公共步骤知识库
- `scripts/sync/*`：平台与本地知识同步、变量备注回写
- `skills/case-skills`：用例分析与 AI 辅助

---

## 强制 SOP（批量建用例必须遵循）

### Phase 0：状态矩阵分析（阻断）

在执行任何批量创建前，必须先完成：

1. 拆解手工用例中的独立状态维度
2. 枚举所有状态组合（笛卡尔积）
3. 输出“状态组合映射表”（组合 -> 公共步骤/API 关键字段）
4. 等待人工审批

未收到 `Approve` / `通过` 前，禁止调用批量创建 API。

### Phase 1：单条契约验证（Fail-Fast）

- 先用 1 条数据验证 `create_step/update_step` 参数格式
- 验证通过后再进入样本创建

### Phase 2：样本创建 + 审计

- 每种组合先建 1 条样本
- 用 `case-debugger` 审计通过后，才能批量创建

### Phase 3：批量创建 + 回写

- 批量创建剩余用例
- 回写 case_id 到飞书
- 产出审计/同步报告归档

---

## 质量卡点（G1/G2/G3）

| 卡点 | 目标 | 产物 |
|---|---|---|
| G1 入参契约清晰化 | SKILL 文档写清参数类型/必填/默认值 | 各 `SKILL.md` |
| G2 API 契约单次验证 | 一次性冒烟验证 case/flow/variable 关键接口 | `sandbox/workspace/contract_report.json` |
| G3 状态维度版本化 | 规则独立维护并用于审计加载 | `knowledge/audit/config_rules.json` + 审计报告 |

执行命令：

```bash
python scripts/verify/contract_smoke.py
python scripts/verify/run_case_debugger_audit.py
```

---

## 平台 API 注意事项

- `method` 必须是整数：`0=GET, 1=POST, 2=PUT, 3=DELETE`
- 平台很多更新动作采用：`GET -> 修改 -> POST`，不是直接 `PUT`
- `POST /case/variable` 更新变量时，body 必须带 `id`
- 批量前必须先做单条验证

---

## 快速开始

### 1. 环境准备

创建 `.env`（可参考 `.env.example`）：

- `TEST_PLATFORM_URL`
- `TEST_PLATFORM_TOKEN`
- `LARK_APP_ID`
- `LARK_APP_SECRET`
- 其他项目依赖变量

### 2. 依赖安装

按子模块需要安装依赖（例如 `agent_service/requirements.txt`，脚本目录依赖等）。

### 3. 常用流程

1. 读取飞书手工用例
2. Phase 0 状态矩阵分析并审批
3. 单条验证 + 样本创建 + 审计
4. 批量创建
5. case_id 回写飞书
6. 同步知识库并归档报告

---

## 目录概览

```text
skills/
  lark-skills/           # 飞书读写能力
  sdet-skills/           # 平台创建/审计/回写能力
  case-skills/           # 用例分析与 AI 辅助
scripts/
  create/                # 创建相关脚本
  sync/                  # 同步/回写脚本
  update/                # 更新类脚本
  verify/                # 契约与审计验证脚本
knowledge/
  common_cases/          # 公共步骤知识库
  audit/                 # 审计规则配置
sandbox/workspace/       # 运行产物与报告
```

---

## 安全与治理

- 禁止在仓库提交真实 token/密钥
- 使用环境变量管理凭据
- 批量执行前保留审计与回滚信息
- 对同步脚本产物进行人工 spot-check

---

## 参考

- 技能索引：`skills/README.md`
- 平台客户端说明：`skills/sdet-skills/platform-client/SKILL.md`
- 设计复盘：`knowledge/case_design/insight.md`
