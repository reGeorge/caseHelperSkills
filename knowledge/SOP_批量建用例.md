# SOP — 自动化用例批量生成标准操作程序

> 版本：v1.2 | 创建日期：2026-03-20 | 更新日期：2026-03-23 | 基于 Zentyal 项目复盘修订
> 适用场景：根据飞书手工用例批量在 SDET 平台创建自动化用例

---

## 一、触发条件

以下任意条件满足即需走本 SOP，**禁止直接跳到代码生成**：

- 用户说"根据手工用例生成自动化用例"
- 用户说"批量建用例 / 批量创建"
- 任务涉及调用 `batch-case-creator` 或 `platform-client.create_case/create_step` 进行批量操作

---

## 二、Phase 0 — 分析与设计（强制人工审批门禁）

### 2.1 输入数据读取与验证（⚡ 新增检查点）

1. 从飞书读取目标 sheet 数据（`LarkSheetReader.read_from_url()`）。
2. **立即断言用例 ID 前缀**：对第一行和最后一行执行正则匹配，确认与用户描述的用例集一致。
   ```python
   import re
   assert re.match(r'^对接zentyal-', rows[0]['case_id']), "数据来源校验失败，请重新拉取"
   ```
3. 不通过则拒绝缓存、重新拉取，绝对不信任本地 `lark_structure.json` 等过期文件。
4. 在分析报告头部注明：`sheet=xxx, 行数=N, ID范围=xxx-001~xxx-038`。

### 2.2 状态维度拆解（State Machine Breakdown）

- 阅读手工用例的**标题、前置条件、操作步骤、预期结果**四个维度。
- 提取所有相互独立的测试维度（如：SSL配置、证书校验方式、认证协议）。
- 区分"**环境基准状态**"（State Machine 层）与"**认证/测试行为**"（打流层）。
- 确认维度组合总数 = 所有独立维度基数之积，与飞书用例数量对齐。

### 2.3 公共步骤完整映射（⚡ 新增检查点）

**对拟引用的全部公共步骤**（包括配置步骤、打流步骤、清理步骤）统一执行：

```
GET /api/sdet-atp/case/{step_id}
```

提取每个步骤的变量清单，整理为三列表格，纳入分析报告中：

| 步骤 ID | 步骤名称 | 变量名 | 默认值 | 用例级需覆盖? |
|:---:|---|---|---|:---:|
| 62033 | 【公共】Portal 认证 | `Portal_username` | `testUser` | ✅ |

> ⚠️ 不同协议步骤的变量名**可能不同**，务必提前核查，不可假设统一。

---

### 2.3.1 实际API确认（⚡ 新增检查点 - v1.2更新）

**在创建公共步骤前，必须先确认实际API接口。**

#### 步骤1: 用户确认或提供API

- 用户主动提供实际API端点和契约信息
- 或通过以下方式获取:
  - API文档
  - Postman测试
  - 已有成功调用记录

#### 步骤2: 记录API契约

创建 `materials/02_actual_api_contract.md` 文件,记录:

1. **已有公共步骤清单**
   - 从 `knowledge/common_cases_manifest.json` 提取
   - 标注哪些步骤已存在、哪些需新建

2. **实际API信息**
   - API端点: `/api/xxx/xxx`
   - 请求方法: GET/POST/DELETE
   - 请求格式: JSON示例
   - 响应格式: JSON示例
   - 错误码和错误消息

3. **关键发现**
   - API范围差异: 初始理解 vs 实际需求
   - 公共步骤精简: 原计划 vs 实际需要
   - 自动化范围调整: 哪些用例可自动化、哪些需UI/人工

#### 步骤3: 更新设计

根据实际API调整:

| 调整项 | 原设计 | 实际需要 |
|-------|--------|---------|
| 公共步骤数量 | 6个 | N个(根据实际API) |
| 可自动化用例 | 18条 | M条(根据可用API) |
| 实施策略 | 全部API自动化 | 混合策略(API+UI+人工) |

#### 步骤4: 更新交互报告

在 `case_coverage_report.html` 中:

1. 更新"公共步骤设计"表格
2. 更新"用例清单"状态(可自动化/需调研)
3. 添加链接到 `materials/02_actual_api_contract.md`
4. 更新统计卡片(实际可自动化用例数)

---

#### 示例: 多业务服务项目

**用户提供信息**:
- 登录管理端step_id: 51401
- 新增业务服务: `/sam/api/admin/businessServer/add`
- 查询业务服务: `/sam/api/admin/businessServer/query`
- 删除业务服务: `/sam/api/admin/businessServer/delete`

**记录到 `02_actual_api_contract.md`**:
```markdown
### API 1: 新增业务服务
**端点**: /sam/api/admin/businessServer/add
**方法**: POST

**请求示例**:
{
  "authBusinessServer": true,
  "businessServerShort": "DYJ",
  "businessServerId": "打印机",
  "businessServerDes": "打印机服务"
}
```

**调整公共步骤**:
- 原计划6个步骤 → 实际需要3个(1个已存在)
- 原设计"业务服务用户管理" → 实际是"业务服务配置管理"

**更新交互报告**:
- 公共步骤: 6个 → 3个
- 可自动化用例: 18条 → 10条
- 需调研用例: 0条 → 8条

---
| 67312 | 【公共】1X GTC | `peap_username` | `testUser` | ✅ |
| … | … | … | … | … |

> ⚠️ 不同协议步骤的变量名**可能不同**，务必提前核查，不可假设统一。

### 2.4 步骤结构明确定义（⚡ 新增检查点）

在分析报告中以 ASCII 图形式明确每类用例的步骤组成：

```
【状态机】用例（负责建立环境）：
  Step 1: [配置公共步骤 ID]

【打流】用例（负责验证行为，不含状态机）：
  Step 1: [认证公共步骤 ID]
  Step 2: [数据清理公共步骤 ID]
```

> 状态机用例与打流用例**完全独立**，打流用例步骤链中**不得引入任何配置步骤**。

### 2.5 多层目录结构设计（Multi-Layer Directory Architecture）

- 根据 2.2 提取的独立维度设计 2-3 层目录结构，避免扁平化。
- 每个叶子节点对应 1 个基准状态组合。
- 示例：`根目录 / SSL状态（4种）/ 协议（4种，仅打流）`

### 2.6 输出分析报告与强制阻断

Phase 0 分析报告包含以下必审内容，缺一不可：

| 必审项 | 说明 |
|---|---|
| 用例ID范围 + 总数 | 与飞书核对 |
| 独立维度拆解 | 每个维度的取值集合 |
| 所有公共步骤变量清单表 | 含 step_id + 变量名 + 默认值 |
| 用例步骤链 ASCII 示意 | 每类用例写一张图 |
| 多层目录结构图 | 含拟建目录名称，`[待确认 ID]` |
| 用例级变量覆盖映射表 | 每种组合的覆盖值，`[待人工确认]` |

输出完毕后，**立即停止所有代码生成**，输出：

> **Phase 0 分析完毕。请核对【维度组合】、【公共步骤变量清单】、【步骤链结构】、【目录结构】是否准确。确认后请回复 `Approve` 或 `通过`，否则我不会执行任何 API 调用或批量创建。**

---

## 三、Phase 1 — 目录结构建立与样本验证（Approve 后执行）

### 3.1 建立目录结构

```python
# 按分析报告中的多层结构逐层创建
client.create_directory(parent_id=ROOT_ID, name="SSL关闭", caseType=0)
# 记录返回的 directory_id，维护 ID 映射字典
```

> 目录创建完成后，在分析报告中填入实际 ID（替换 `[待确认 ID]`）。

### 3.2 建立公共步骤（若尚未存在）

- 检查 `knowledge/common_cases_manifest.json`，确认所需步骤是否已存在。
- 若需新建，参照 Phase 0 变量清单创建，**注入真实环境变量**（IP/域名/管理员账号等），
  不得使用占位符如 `your-server-ip`。
- 建完后运行同步：`python scripts/sync/sync_knowledge_from_platform.py`，更新本地知识库。

### 3.3 每类分支建 1-2 条样本用例

- 优先选最简单的叶子节点（如"关闭SSL + Portal"）建第一条样本。
- 用 `GET /case/{id}` 查询返回结果，人工核查：
  - [ ] 步骤链是否正确（步骤数量、引用 ID）
  - [ ] 用例级变量是否全部覆盖
  - [ ] 变量值无硬编码（用变量名而非明文账号/IP）

> 样本通过审计后，才能批量创建同分支其余用例。

---

## 四、Phase 2 — 批量创建

### 4.1 编写批量创建脚本

脚本命名规范：`sandbox/create_phase1_bulk.py`（或 `create_phase2_xxx.py`）

脚本结构：
1. 定义用例矩阵（列表/字典），包含每条用例的 `name`、`parent_id`、`step_ids[]`、`variables{}`
2. 循环调用 `client.create_case()` + `client.create_step()`
3. 收集结果，打印 `case_id` 或失败原因
4. **先 dry-run（只 print 不 POST）**，确认矩阵完整性后再实际执行

### 4.2 执行与验证

```bash
python sandbox/create_phase1_bulk.py
```

执行完毕后：
1. 检查输出中是否有失败条目，逐条排查
2. 在平台 UI 抽查 2-3 条用例，确认步骤链与变量
3. 将所有成功的 `case_id` 记录到分析报告对应表格

---

## 五、收尾流程（每次批量创建后必执行）

### 5.1 飞书 ID 回写

```bash
python scripts/sync/writeback_xxx.py
```

回写后打开飞书表格目视确认 ID 列已填入，无空白格。

### 5.2 分析报告归档更新

- 在分析报告中将对应 Phase 标注为 ✅ 已完成
- 填入所有实际 case_id（替换"待批量创建"等占位文字）
- 更新步骤描述（与实际步骤链保持一致）

**分析报告归档路径：**
```
workspace/analysis/{YYYYMMDD}_{主题}/{YYYYMMDD}_{HHMMSS}_case_design_analysis.md
```

### 5.3 Sandbox 清理

执行完毕的一次性脚本前缀改为 `_done_` 或直接删除：
- `_tmp_*.py` — 全部删除
- 单次调试用脚本（inspect_/dump_/check_等）— 用完即删
- 保留：`create_phase*.py`、`fetch_xxx.py`、`audit_xxx.py`、`parameterize_xxx.py`

### 5.4 知识库同步

若本次新增或修改了公共步骤：

```bash
python scripts/sync/sync_knowledge_from_platform.py
git diff knowledge/
# 目视确认字段变更合理
```

### 5.5 Git 提交

commit message 模板：
```
feat({主题}): Phase N 完成 - {用例数}条{分类}用例

- 创建 N 个子目录（ID1-IDN）
- 状态机用例: IDa-IDb（描述）
- 打流用例: IDc-IDd（描述，步骤链格式）
- 公共步骤：注入真实环境（IP/域名/账号）
- 变量参数化：列出关键变量名
```

---

## 六、平台 API 使用规范

| 规范 | 说明 |
|---|---|
| `method` 字段类型 | **整数**：0=GET, 1=POST, 2=PUT, 3=DELETE，不是字符串 |
| 更新模式 | **GET → 修改字段 → POST 集合端点**，平台不支持直接 PUT |
| body 序列化 | 只在 `platform_client` 内部做一次，调用方传 dict 即可 |
| 批量前验证 | 批量操作前，永远先单条验证 API 参数格式 |
| 错误处理 | 遇到 4xx/5xx 立即停止并打印完整响应，不要 retry 相同参数 |
| 目录创建 | `caseType=0` |
| 用例变量注入 | 通过 `case_variables` 字段，`type=1` 为字符串，`type=3` 为从响应提取 |

---

## 七、检查清单（每次 Phase 0 完成时对照）

- [ ] 飞书数据已读取并通过 ID 前缀格式断言
- [ ] 用例 ID 总数与范围已确认
- [ ] 所有公共步骤（配置/打流/清理）的 step_id 已确认
- [ ] 每个公共步骤的变量清单已提取并整理为表格
- [ ] 步骤链 ASCII 示意图已输出并经用户确认
- [ ] 多层目录结构图已输出并经用户确认
- [ ] 用例级变量覆盖映射表已输出
- [ ] 已等待用户 Approve，未自行开始批量创建

---

## 附录：常见公共步骤参考

| 场景 | step_id | 变量名（用户名/密码） |
|---|:---:|---|
| 有线 Portal 认证+记账 | 62033 | `Portal_username` / `Portal_password` |
| 有线 1X PEAP(GTC) | 67312 | `peap_username` / `peap_password` |
| 有线 1X TTLS-PAP | 67313 | `peap_username` / `peap_password` |
| 有线 1X PEAP(MschapV2) | 67314 | `peap_username` / `peap_password` + `src_username` |
| 数据清理（销户） | 55645 | — |
| 开户（Radius） | 见 manifest | `auth_username` / `auth_password` |

> 公共步骤完整列表见 `knowledge/common_cases_manifest.json`

---

*本文档由 Zentyal 项目复盘自动生成，下次迭代后请同步更新附录与检查清单。*
