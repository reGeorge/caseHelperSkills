# NAC 对接Zentyal — 自动化设计分析报告

> 分析时间: 2026-03-19（修订 2026-03-19）| 手工用例: **37 条**（对接zentyal-001~038，缺-024）| 来源: NAC V5.1R26.03S01-对接Zentyal-TP | sheet=kQHpSt

---

## 一、设计者在想什么

读完这 37 条用例（对接zentyal-001~038，缺 024），能感受到设计者的思维是分层的，不是随机堆砌的。大致分了三个关注点，彼此边界很清晰：

### 1.1 第一层：这个配置页面本身靠不靠谱（001-007）

最前面 7 条都是在问一件事：Zentyal 认证源的 SSL 配置表单，各个字段的校验逻辑对不对。比如主服务器域名是否必填、证书文件后缀/大小的限制、SSL 开关和端口的联动。

这一层本质上是**配置界面的合法性验证**，跟 Zentyal 服务器本身通不通没关系，纯粹是在测 UNC 侧的表单逻辑。用例写得比较零散（有的一步搞定，有的五步混杂），体现出设计者是边改需求边补用例的，不像一次性系统设计出来的。

### 1.2 第二层：SSL 通道打得开吗（008-023 认证学习矩阵）

这 16 条用例的结构非常规整，背后是一个**二维矩阵**：

```
SSL 状态（4种）× 认证协议（4种）= 16 个格子

SSL状态：
  ├── 关闭SSL                    → 008~011
  ├── SSL+关闭证书校验             → 012~015
  ├── SSL+公有证书校验             → 016~019
  └── SSL+自签名证书校验           → 020~023

认证协议（每种SSL状态各4种）：
  ├── Portal
  ├── 1x GTC
  ├── 1x MschapV2
  └── 1x TTLS   ← 已在飞书中登记，无需额外补充
```

每个格子的断言都一样：认证成功，用户已学习到本地。设计者关心的是"这条链路在不同 SSL 配置下都能打通吗"，典型的**环境基准状态矩阵**思路，非常适合自动化。

> ⚠️ 注意：与 AD/LDAP 表不同，Zentyal 表**没有**"单域/父子域/主备域"三种域类型维度，一台 Zentyal 服务器就是一种配置，不存在多域类型变量差异。

### 1.3 第三层：用户组映射算法算对了吗（025-038）

这是整批用例里设计含金量最高的部分。设计者在验证一个"向祖先溯回、找最近映射"的算法，具体来说就是：用户属于某个 OU，如果这个 OU 没有映射关系，系统应该往上找父 OU，直到找到有映射的为止，找不到就落入缺省用户组。

设计者系统性地构造了各种场景：

- 安全组模式（不走 OU 层级，走安全组）（025-026）
- 往上溯 1 级/2 级/3 级/4 级/7 级找到映射（027-031）
- 用户组下级组有映射，自身无映射，学习用户组（032）
- 用户组有映射，上级组也有映射，学习用户组（033）
- 用户组有映射，下级组也有映射，学习用户组（034-035）
- 映射关系实时变更后，已在线用户的用户组是否跟着更新（036-037）
- 038：用户所属组未映射，学习上级组（对应 027 的相似场景）

这部分测试的是一个有状态的算法，有些场景需要多轮操作才能观测到结果变化，自动化成本高，但逻辑可参数化。

---

## 二、模块划分与自动化可行性

| 模块 | 用例范围 | 核心关注点 | 自动化可行性 |
|------|---------|-----------|------------|
| SSL 配置字段校验 | 对接zentyal-001~007 | 表单合法性，UI 反馈 | ⚠️ 偏 UI 操作，API 能覆盖大部分，但有文件上传场景 |
| SSL×协议 认证矩阵 | 对接zentyal-008~023（16条）| 认证链路联通性 | ✅ 核心可自动化区域，结构最规整 |
| 安全组用户同步 | 对接zentyal-025~026 | 安全组+用户组 | ⚠️ 需确认靶机是否支持安全组模式 |
| 模糊映射算法验证 | 对接zentyal-027~035, 038 | 祖先溯回逻辑 | ✅ OU 层级可参数化，逻辑清晰 |
| 映射变更实时更新 | 对接zentyal-036~037 | 在线用户用户组的实时追踪 | 🟡 高成本，依赖框架支持多轮断言 |

---

## 三、公共步骤需求清单

### 3.1 知识库现状核查

| 步骤语义名 | 知识库状态 | ID | syncOrganizationType | 覆盖用例 |
|-----------|-----------|-----|-----|------|
| 查询身份源 | ✅ 已有 | 66558 | — | 各场景 Teardown 前查询确认 |
| 删除指定名称的身份源 | ✅ 已有 | 66559 | — | 各场景 Teardown 清理用 |
| 新增并更新Zentyal认证源（关闭SSL） | ✅ 已有 | 68277 | — | 覆盖 对接zentyal-008~011 |
| 新增并更新Zentyal认证源（SSL+不校验证书） | ✅ 已有 | 68278 | — | 覆盖 对接zentyal-012~015 |
| 新增并更新Zentyal认证源（SSL+公有证书校验） | ✅ 已有 | 68279 | — | 覆盖 对接zentyal-016~019 |
| 新增并更新Zentyal认证源（SSL+自签名证书校验） | ✅ 已有 | 68280 | — | 覆盖 对接zentyal-020~023 |
| 通用Zentyal-AD源配置模板 | ✅ 已有 | 68274 | — | 全参数化基准模板 |
| 新增并更新Zentyal认证源（**安全组模式**+缺省用户组+自动更新） | ✅ 已有 | 68281 | `group` ✅ | 覆盖 **对接zentyal-025~026** |
| 新增并更新Zentyal认证源（**OU模式**+OU映射脚本） | ✅ 已有 | 68282 | `ou` ✅ | 覆盖 **对接zentyal-027~038** |

> **实测发现（2026-03-19 审计）**：
> - 68281 的 `syncOrganizationType = "group"` + `organizationMapScript = {}` — 已覆盖安全组(group)映射场景，用例级仅需覆盖 `organizationMapScript`（填入安全组→本地组的映射 JSON）和 `existsAutoUpdateUserGroup`/`autoUpdateUserTemplate` 开关
> - 68282 的 `syncOrganizationType = "ou"` + `organizationMapScript = {}` — 已覆盖 OU 层级模糊映射场景，用例级仅需覆盖 `organizationMapScript`（填入 OU 路径→本地组的映射 JSON）
> - **所有公共步骤的分工已对齐**，无需新增公共步骤

**Zentyal 认证源无多域类型区分**（不同于 AD/LDAP 对接，Zentyal 只有一台服务器，不存在"单域/父子域/主备域"概念）。现有 4 条公共步骤已将所有差异化字段参数化，批量建用例时不需要引入额外的域类型变量。

**结论：所有公共步骤已全部落地并入库（9条），公共步骤分工已对齐。可直接进入 Phase 1/2 批量创建。**

---

### 3.2 公共步骤人机协作建设流水线

> 缺失的公共步骤不能由 AI 凭空捏造 body 结构，必须基于人工在平台上创建的真实用例学习后生成。每一条走如下 5 步，**不跳步，不并行**。

```
Step A  [人工]  在自动化平台手动创建一条公共步骤用例
        ├── 命名规范：「【公共】新增Zentyal认证源」（含具体SSL状态后缀）
        ├── 关键要求：所有业务字段全部参数化，不硬编码任何值
        │     参考变量清单（以关闭SSL版为例）：
        │       zentyal_host       - Zentyal 服务器地址
        │       zentyal_port       - 端口（关闭SSL时为389）
        │       zentyal_username   - 绑定账号
        │       zentyal_password   - 绑定密码
        │       zentyal_base_dn    - 搜索根DN
        │       zentyal_ssl        - SSL开关（false）
        └── 完成后提供 case_id 给 AI

Step B  [AI]   读取平台上该 case 的完整结构
        ├── GET /case/{id} 获取用例体
        ├── GET /case/variables/{id} 获取变量列表
        └── GET /flow/{id} 获取步骤序列

Step C  [AI]   学习 + 核查 + 输出对照表
        ├── 对照本需求的参数化要求，核查变量是否覆盖所有注入点
        ├── 识别遗漏字段或命名不规范项
        └── 输出「步骤结构对照表」：
              变量名 | 当前默认值 | 覆盖用例 | 是否缺失/需调整

Step D  [人工]  审阅对照表，按建议在平台上补齐或调整用例

Step E  [AI]   确认结构达标后，写入知识库 manifest.json，后续批量脚本直接引用此 ID
```

**本批次需走流水线的步骤（按优先级）：**

| 优先级 | 步骤名称 | 覆盖用例数 | 人工预估耗时 | 备注 |
|--------|---------|-----------|------------|------|
| P0 | 新增Zentyal认证源（关闭SSL） | 16（008-023 + 模糊映射前置） | ~30min | 最先做，其他三条可在此基础上复制微调 |
| P0 | 新增Zentyal认证源（SSL+不校验证书） | 4（012-015） | ~15min | 复制关闭SSL版，调整 ssl=true, certVerify=false |
| P0 | 新增Zentyal认证源（SSL+公有证书校验） | 4（016-019） | ~15min | 在上一条基础上增加 certVerify=true, certType=public |
| P0 | 新增Zentyal认证源（SSL+自签名证书） | 4（020-023） | ~15min | 增加 certType=self-signed, certFile 变量 |
| P1 | 修改Zentyal认证源（上传用户组映射关系） | 12（027-038） | ~20min | 注意 mappingFile 是文件路径还是内容需确认 |
| P1 | 修改Zentyal认证源（缺省组 + 自动更新开关） | 3（032, 036-037） | ~10min | defaultGroup 和 autoUpdateGroup 两个参数 |

> P0 四条逻辑高度相似，建议先把"关闭SSL"版本完整走一遍流水线验收，其余三条复制调整，能节省大量时间。

---

## 四、需要单独处理的非典型用例

### 4.1 🔴 BLOCKER：006 — 证书文件上传字段校验

**为什么特殊：** 步骤 3-4 需要通过文件选择器上传证书（后缀校验 + 大小校验），这是纯 UI 文件系统交互，自动化框架无法通过 API 模拟。

**建议方案：**
- 优先确认是否存在 `POST /cert/upload` 或类似的证书上传 API 接口，如果有，改写为 API 形式创建自动化用例
- 如果确实只有 UI 路径，本条保留手工执行，不纳入自动化批次

**涉及的校验点：**
1. 后缀不是 `.crt` → 上传失败并提示后缀名无效
2. 文件大小超过 16MB → 上传失败并提示大小超限
3. 正确证书 → 上传成功
4. 删除证书 → 二次确认弹窗
5. 自签名切换回公有证书 → 修改成功

---

### 4.2 🟡 高成本：005 — 单条用例跨五个配置状态

**为什么特殊：** 这条用例在一条里混合了五个不同操作（开SSL → 开证书校验 → 改证书类型 → 不上传证书保存 → 关SSL），每步断言不同，不是一个单纯的"前置+执行+断言"结构。

**建议方案：** 这条用例实际上是一个配置修改的"探索流程"，建议拆分为独立用例（对应配置项变更场景），或保留手工执行作为冒烟用例，不单独建自动化用例。

---

### 4.3 🟡 高成本：036-037 — 映射变更实时追踪

**为什么特殊：** 这两条用例要求用户已在线后，每次修改映射关系，都要断言在线用户的用户组跟着变化。涉及多轮"操作-观测"循环（036 有 9 步操作+断言），且每次观测依赖的是用户组的实时刷新，框架需要支持循环等待或状态轮询。

**建议方案：**
- 评估测试框架是否支持多轮状态断言；如果支持，可以参数化映射变更操作，循环执行
- 如果框架不支持，先保留手工，等映射基础用例自动化稳定后再考虑

---

### 4.4 ⚠️ 需确认：023 — TTLS 协议需要额外设置默认协议

023 比其他 TTLS 用例（011、015、019）多了"进入认证管理/认证证书配置，修改1x认证默认协议：EAP-TTLS"这一步。其他三个 TTLS 用例没有这步，但都标注了认证成功。

**需人工确认：** 这个设置步骤是仅在自签名证书场景下才需要，还是其他用例的步骤遗漏了？确认后再决定是否把这步单独抽成公共步骤前置。

---

## 五、实施路线图

### ✅ Phase 0（已完成）：人工准备公共步骤

| 用例名 | ID | ssl_enable | cert_check | cert_type | port |
|---|:---:|:---:|:---:|:---:|:---:|
| 新增并更新Zentyal认证源（关闭SSL） | 68277 | false | false | 0 | 389 |
| 新增并更新Zentyal认证源（SSL+不校验证书） | 68278 | true | false | 0 | 636 |
| 新增并更新Zentyal认证源（SSL+公有证书校验） | 68279 | true | true | 0 | 636 |
| 新增并更新Zentyal认证源（SSL+自签名证书校验） | 68280 | true | true | 1 | 636 |
| 通用Zentyal-AD源配置模板 | 68274 | — | — | — | — |

> 全部审计通过（硬编码问题 = 0），已写入 `knowledge/common_cases_manifest.json`。

### ✅ Phase 1（已完成）：SSL×协议 认证矩阵（20条）

**目标目录：68276** | 完成时间：2026-03-19

#### 用例结构设计（状态机与打流分离）

每个 SSL 子目录包含：
- **1 条【状态机】用例**：仅引用 AD 配置公共步骤，负责建立/更新认证源环境，独立运行
- **4 条【打流】用例**：认证步骤 → 数据清理（不含状态机，状态机独立管理）

**打流公共步骤映射：**
| 认证协议 | 变量名 | 公共步骤 ID | 公共步骤名称 |
|---|---|:---:|---|
| Portal | `Portal_username` / `Portal_password` | **62033** | 【公共】【认证】【记账】有线二代Portal认证+记账开始+下线 |
| 1x GTC | `peap_username` / `peap_password` | **67312** | 【公共】【认证】有线1X-PEAP（GTC） |
| 1x MschapV2 | `peap_username` / `peap_password` + `src_username` | **67314** | 【公共】【认证】有线1X-PEAP（MSCHV2） |
| 1x TTLS | `peap_username` / `peap_password` | **67313** | 【公共】【认证】有线1X（TTLS-PAP） |
| 数据清理 | — | **55645** | 【公共】【数据清理】【销户】 |

**用例级变量覆盖（所有打流用例统一）：**
| 变量名 | 值 | 适用协议 |
|---|---|---|
| `Portal_username` | `xujitian` | Portal |
| `Portal_password` | `shyfzx@163` | Portal |
| `peap_username` | `xujitian` | GTC / MschapV2 / TTLS |
| `peap_password` | `shyfzx@163` | GTC / MschapV2 / TTLS |
| `src_username` | `xujitian` | MschapV2 额外字段 |
| `ssid` | `ADZentyal` | 全部 |
| `userId2test` | `xujitian` | 全部 |

**完整用例清单：**

| 子目录 | 目录ID | 类型 | 飞书ID | case_id | 协议 | 步骤链 |
|---|:---:|---|---|:---:|---|---|
| 关闭SSL | **68287** | 【状态机】 | — | **68291** | — | AD配置(68277) |
| 关闭SSL | 68287 | 【打流】 | 对接zentyal-008 | **68300** | Portal | 62033→55645 |
| 关闭SSL | 68287 | 【打流】 | 对接zentyal-009 | **68299** | GTC | 67312→55645 |
| 关闭SSL | 68287 | 【打流】 | 对接zentyal-010 | **68301** | MschapV2 | 67314→55645 |
| 关闭SSL | 68287 | 【打流】 | 对接zentyal-011 | **68302** | TTLS | 67313→55645 |
| SSL+关闭证书校验 | **68288** | 【状态机】 | — | **68292** | — | AD配置(68278) |
| SSL+关闭证书校验 | 68288 | 【打流】 | 对接zentyal-012 | **68303** | Portal | 62033→55645 |
| SSL+关闭证书校验 | 68288 | 【打流】 | 对接zentyal-013 | **68304** | GTC | 67312→55645 |
| SSL+关闭证书校验 | 68288 | 【打流】 | 对接zentyal-014 | **68305** | MschapV2 | 67314→55645 |
| SSL+关闭证书校验 | 68288 | 【打流】 | 对接zentyal-015 | **68306** | TTLS | 67313→55645 |
| SSL+公有证书校验 | **68289** | 【状态机】 | — | **68293** | — | AD配置(68279) |
| SSL+公有证书校验 | 68289 | 【打流】 | 对接zentyal-016 | **68307** | Portal | 62033→55645 |
| SSL+公有证书校验 | 68289 | 【打流】 | 对接zentyal-017 | **68308** | GTC | 67312→55645 |
| SSL+公有证书校验 | 68289 | 【打流】 | 对接zentyal-018 | **68309** | MschapV2 | 67314→55645 |
| SSL+公有证书校验 | 68289 | 【打流】 | 对接zentyal-019 | **68310** | TTLS | 67313→55645 |
| SSL+自签名证书校验 | **68290** | 【状态机】 | — | **68294** | — | AD配置(68280) |
| SSL+自签名证书校验 | 68290 | 【打流】 | 对接zentyal-020 | **68311** | Portal | 62033→55645 |
| SSL+自签名证书校验 | 68290 | 【打流】 | 对接zentyal-021 | **68312** | GTC | 67312→55645 |
| SSL+自签名证书校验 | 68290 | 【打流】 | 对接zentyal-022 | **68313** | MschapV2 | 67314→55645 |
| SSL+自签名证书校验 | 68290 | 【打流】 | 对接zentyal-023 | **68314** | TTLS | 67313→55645 |

### ✅ Phase 2b（已完成）：OU模糊映射算法用例（027-035, 038）

**目标目录：68329（OU映射模糊查找算法）** | 完成时间：2026-03-20

| 飞书ID | 类型 | case_id | 用户 | 映射规则 | 期望用户组 | 验证逻辑 |
|---|---|:---:|---|---|---|---|
| — | 【状态机】027 | **68330** | Zentyal_test01 | ABCDEFGH→testABCDEFGH | testABCDEFGH | 溯1级命中 |
| 对接zentyal-027 | 【打流】 | **68331** | Zentyal_test01 | — | testABCDEFGH | GTC+清理 |
| — | 【状态机】028 | **68333** | Zentyal_test02 | test AB→testAB | testAB | 溯2级命中 |
| 对接zentyal-028 | 【打流】 | **68334** | Zentyal_test02 | — | testAB | GTC+清理 |
| — | 【状态机】029 | **68335** | Zentyal_test02 | test A→testA | testA | 溯3级命中 |
| 对接zentyal-029 | 【打流】 | **68336** | Zentyal_test02 | — | testA | GTC+清理 |
| — | 【状态机】030 | **68337** | Zentyal_test02 | test(根)→testRoot | testRoot | 溯4级命中(根OU) |
| 对接zentyal-030 | 【打流】 | **68338** | Zentyal_test02 | — | testRoot | GTC+清理 |
| — | 【状态机】031 | **68339** | Zentyal_test01 | test AB→testAB | testAB | 溯7级命中 |
| 对接zentyal-031 | 【打流】 | **68340** | Zentyal_test01 | — | testAB | GTC+清理 |
| — | 【状态机】032 | **68341** | Zentyal_test02 | test ABCDE→testABCDE（子节点，不触发溯回）| yy（缺省组）| 全祖先链无映射 |
| 对接zentyal-032 | 【打流】 | **68342** | Zentyal_test02 | — | yy（缺省组）| GTC+清理 |
| — | 【状态机】033 | **68343** | Zentyal_test02 | test ABC→testABC + test ABCD→testABCD | testABCD | 自身命中优先于父 |
| 对接zentyal-033 | 【打流】 | **68344** | Zentyal_test02 | — | testABCD | GTC+清理 |
| — | 【状态机】034 | **68345** | Zentyal_test02 | test ABCD→testABCD + test ABCDE→testABCDE（子节点）| testABCD | 自身命中，子节点不干扰 |
| 对接zentyal-034 | 【打流】 | **68346** | Zentyal_test02 | — | testABCD | GTC+清理 |
| — | 【状态机】035 | **68347** | Zentyal_test02 | 同034规则顺序互换 | testABCD | 规则顺序幂等 |
| 对接zentyal-035 | 【打流】 | **68348** | Zentyal_test02 | — | testABCD | GTC+清理 |
| — | 【状态机】038 | **68349** | Zentyal_test01 | Step1=68280(SSL+自签名)+Step2=68282(OU) | testABCDEFGH | 溯1级+SSL |
| 对接zentyal-038 | 【打流】 | **68350** | Zentyal_test01 | — | testABCDEFGH | GTC+清理 |

> **032 注意**：`autoAllocationUserGroupId`（缺省用户组ID）需在平台手动配置为对应"yy"用户组的 ID；organizationMapScript 中的 test ABCDE 为子节点，不触发溯回。

> **038 注意**：状态机使用2步设计（68280→68282），需验证第二步是否会覆盖第一步的SSL配置。如有冲突，可改为68282单步 + 用例级SSL变量覆盖。

### Phase 2a：安全组映射用例批量创建（025-026）

**目标目录：68276** | 引用公共步骤：68281（syncOrganizationType = "group"）

| 飞书用例ID | 用例名称 | 用例级变量覆盖 |
|---|---|---|
| 对接zentyal-025 | 用户组类型为安全组（有映射关系） | `organizationMapScript` = 安全组→本地组映射JSON；`auth_username` = test04；`expected_user_group` = groupA |
| 对接zentyal-026 | 用户组类型为安全组（无映射关系） | `organizationMapScript` = 安全组→本地组映射JSON（不含 group D）；`auth_username` = test06；`expected_user_group` = root（缺省） |

> 样本 case_id = **68284**（对接zentyal-025），创建于 2026-03-19。待人工审计步骤结构后再创建 026。

### Phase 2b：OU模糊映射算法用例批量创建（027-035, 038）

1. 先建 1 条最简单的（027，单层溯回，引用68282），验证 OU 路径映射脚本格式可行
2. 批量创建剩余用例：028-031（溯2/3/4/7级）、032-035（命中优先级）、038（引用68280，开启SSL场景）
3. 36-037（映射变更实时追踪）：引用68281（auto_update=true），单独处理

### Phase 3：非典型用例处置

- 006：确认是否有 API 上传接口，有则改写，无则标注手工
- 005：拆分或标注手工冒烟（5步混杂，不建议单独自动化）
- 036-037：引用68281并设 `existsAutoUpdateUserGroup=true`，框架评估是否支持多轮断言
- 全量完成后回写 case_id 到飞书，更新知识库 manifest

---

## 六、测试数据准备

### 6.1 安全组场景（对接zentyal-025 ~ 026）

#### Zentyal 服务器侧（靶机预置）✅ 已创建（2026-03-20）

| 对象 | 名称 | 密码 | 说明 |
|---|---|---|---|
| 安全组 | group A | — | 有映射，映射到本地组 groupA |
| 安全组 | group B | — | 有映射，映射到本地组 groupB |
| 安全组 | group C | — | 有映射，映射到本地组 groupC |
| 安全组 | group D | — | **无映射**（026 场景用，应落入缺省组） |
| 域用户 | test04 | `zentyal@123` | CN=Users；已加入 group A（025 场景） |
| 域用户 | test06 | `zentyal@123` | CN=Users；已加入 group D（026 场景，无映射） |

#### UNC 侧配置

| 配置项 | 值 |
|---|---|
| `syncOrganizationType` | `group`（68281 默认已设置） |
| `organizationMapScript` | `{"zentyal-domain.lan/safe1":"groupA","zentyal-domain.lan/safe2":"groupB","zentyal-domain.lan/safe3":"groupC"}` |
| 缺省用户组 | `root` |
| 自动更新用户组 | `false`（025-026 不需要） |

#### 用例变量映射

| 用例 | `auth_username` | `auth_password` | `expected_user_group` |
|---|---|---|---|
| 025（有映射） | `test04` | `zentyal@123` | `groupA` |
| 026（无映射） | `test06` | `zentyal@123` | `root`（缺省组） |

---

### 6.2 OU 模糊映射场景（对接zentyal-027 ~ 038）

#### Zentyal 服务器侧 — OU 层级结构（靶机预置）✅ 已创建（2026-03-20）

```
zentyal-domain.lan (根)
├── test (根 OU)
│   ├── test A
│   │   └── test AB > test ABC > test ABCD > test ABCDE
│   │       └── test ABCDEF > test ABCDEFG > test ABCDEFGH > test ABCDEFGHI
│   ├── test B
│   │   └── test BB > test BBB
│   └── test C
│       └── test CC
```

> 注：以上 15 个 OU 均已通过 samba-tool 在 172.17.9.183 创建并验证，层级结构与文档一致。

#### 测试用户 ✅ 已创建（2026-03-20）

| 用户名 | 密码 | 所属 OU（服务器实测 DN） | 用于用例 |
|---|---|---|---|
| Zentyal_test01 | `zentyal@123` | OU=test ABCDEFGHI（最深叶子，祖先链长度9级）| **027, 031, 038** |
| Zentyal_test02 | `zentyal@123` | OU=test ABCD（祖先链长度4级） | **028~030, 032~035** |

> ⚠️ test04、test06 实际在 `CN=Users`（系统默认容器），不在任何 OU 下，属于安全组场景，不涉及 OU 映射算法。

#### 映射脚本格式（syncOrganizationType = "ou"）

```json
{
  "ZENTYAL.RUISHAN.CC/test/test A/test AB": "testAB",
  "ZENTYAL.RUISHAN.CC/test/test A/test AB/test ABC": "testABC"
}
```

> ⚠️ **待实测确认**：`organizationMapScript` key 格式（`域名/OU/子OU` 斜杠路径 vs LDAP DN 格式）在首条样本对接时通过靶机验证确认，确认后填入下方矩阵的正式 key 值。路径前缀域名统一用 `ZENTYAL.RUISHAN.CC`（大写，域名大小写敏感）。

#### 用例级变量覆盖矩阵

| 用例 | 映射规则（OU路径→本地组） | 被测用户 OU | 期望落入用户组 |
|---|---|---|---|
| 用例 | 用户 | 用户 OU | 注入映射规则 | 期望用户组 | 验证逻辑 |
|---|---|---|---|---|---|
| 027 | Zentyal_test01 | test ABCDEFGHI | `test ABCDEFGH → testABCDEFGH`（ABCDEFGHI 无映射）| testABCDEFGH | 溯1级命中 |
| 028 | Zentyal_test02 | test ABCD | `test AB → testAB`（test ABCD、test ABC 无映射）| testAB | 溯2级命中 |
| 029 | Zentyal_test02 | test ABCD | `test A → testA`（test ABCD、test ABC、test AB 无映射）| testA | 溯3级命中 |
| 030 | Zentyal_test02 | test ABCD | `test → testRoot`（test ABCD~A 无映射）| testRoot | 溯4级命中（根OU） |
| 031 | Zentyal_test01 | test ABCDEFGHI | `test AB → testAB`（ABCDEFGH~ABC 无映射）| testAB | 溯7级命中 |
| 032 | Zentyal_test02 | test ABCD | `test ABCDE → testABCDE`（ABCDE 是 ABCD 的**子**，非祖先，全祖先链无映射）| yy（缺省组）| 子节点映射不触发，落缺省 |
| 033 | Zentyal_test02 | test ABCD | `test ABC → testABC` + `test ABCD → testABCD` | testABCD | 自身命中，优先于父 |
| 034 | Zentyal_test02 | test ABCD | `test ABCD → testABCD` + `test ABCDE → testABCDE` | testABCD | 自身命中，子节点映射不干扰 |
| 035 | Zentyal_test02 | test ABCD | `test ABCDE → testABCDE` + `test ABCD → testABCD` | testABCD | 同 034，规则顺序不影响结果 |
| 038 | Zentyal_test01 | test ABCDEFGHI | `test ABCDEFGH → testABCDEFGH`，SSL+自签名证书 | testABCDEFGH | 溯1级 + SSL场景 |

#### 祖先链速查

| 用户 | OU 祖先链（由近到远） |
|---|---|
| Zentyal_test01 (ABCDEFGHI) | ABCDEFGH(1)→G(2)→F(3)→E(4)→D(5)→C(6)→AB(7)→A(8)→test(9) |
| Zentyal_test02 (ABCD) | ABC(1)→AB(2)→A(3)→test(4) |

#### 缺省用户组配置

| 场景 | 缺省组名称 | 说明 |
|---|---|---|
| 032 | `yy` | 全祖先链无映射；test ABCDE 映射无效（是子节点，非祖先） |
| 其他 | 任意（不影响断言）| 这些用例期望命中某个映射，缺省组不会被触发 |

---

### 6.3 映射实时更新场景（对接zentyal-036 ~ 037）

| 前置配置 | 值 |
|---|---|
| `existsAutoUpdateUserGroup` | `true`（需在68281中通过用例变量覆盖） |
| 被测用户 | Zentyal_test02 / `zentyal@123`（属于 OU=test ABCD，已创建） |

> ⚠️ 038 与 027 是同一逻辑的 SSL 变体：038 额外要求开启 SSL+自签名证书，在步骤级需引用 68280（自签名SSL公共步骤）而非 68277（关闭SSL），两者步骤链不同，需单独处理。

---

## 七、Skills 流程反思（2026-03-19）

本次项目在执行过程中暴露了四个系统性问题，记录于此作为后续 SOP 优化依据。

---

### 7.1 打流步骤 ID 未在 Phase 0 纳入确认清单

**问题描述**：Phase 0 分析时，只关注了"AD 配置"类公共步骤的建设，完全没有把"认证打流"步骤的 ID 纳入 Phase 0 确认环节。到建第一批样本时，才发现需要 Portal/GTC/MschapV2/TTLS 对应的公共步骤 ID，被迫临时请用户提供（62033、67312、67313、67314）。

**根因**：Phase 0 的"步骤需求清单"只覆盖了 AD 配置侧，漏掉了认证侧。Phase 0 应当对整个步骤链从头到尾建立映射，包括：AD配置步骤 → 认证打流步骤 → 数据清理步骤。

**改进措施**：Phase 0 分析报告中增加"完整步骤链需求清单"，逐类型（配置/打流/清理）列举所需公共步骤，并标注"待确认 ID"项，强制在 Approve 前完成 ID 核实。

---

### 7.2 步骤结构反复调整了两轮才定型

**问题描述**：用例的步骤链经历了三个版本：

- **版本 1**（初始设计）：AD配置 + Portal认证 + 清理（3步，混在一条用例内）
- **版本 2**（用户提出状态机/打流分离后）：状态机用例（AD配置） + 打流用例（AD配置+认证+清理）——打流用例中仍含 AD 配置步骤
- **版本 3**（最终）：打流用例 = 认证 + 清理（2步），**不引入任何 AD 配置步骤**

版本 2 到版本 3 的调整导致已建的 Portal 打流样本（68295-68298）被删除重建，浪费了约 1 小时。

**根因**：建第一条样本之前，没有以书面方式明确"每条用例包含哪些步骤"，对"状态机与打流分离"的含义理解有偏差，认为打流用例只是"额外引入了 AD 配置步骤"，而不是"完全不含 AD 配置步骤"。

**改进措施**：在 Phase 0 分析报告中增加"用例步骤结构设计"与"步骤链 ASCII 示意图"，和用户确认每种用例类型的步骤组成，再启动创建。

---

### 7.3 协议变量名未提前检查

**问题描述**：GTC 用的是 `peap_username`/`peap_password`，Portal 用的是 `Portal_username`/`Portal_password`，MschapV2 额外还有 `src_username`。这些差异直到第一条 GTC 样本（68299）变量设置完成后，建 Portal 时才被意识到需要重新核查，导致不同协议变量注入路径不同，增加了批量创建脚本的复杂度。

**根因**：在 Phase 0 确认公共步骤时，只验证了 AD 配置步骤的变量结构，未对打流步骤执行相同的变量清单检查（`GET /case/{id}` 查看 params 字段）。

**改进措施**：Phase 0 分析阶段，对所有涉及的公共步骤（包括打流步骤）统一执行 `GET /case/{id}` 提取变量清单，整理成"变量名-默认值-是否需要用例级覆盖"三列表格后，纳入 Phase 0 分析报告，作为 Approve 必审内容。

---

### 7.4 Feishu 缓存数据读错表，基于错误数据生成了初版报告

**问题描述**：`sandbox/lark_structure.json` 中缓存的是另一张表（AD LDAPs 表）的数据，导致报告第一版基于"AD对接支持LDAPs-xxx"格式用例生成，整个分析方向偏移。发现时需要重新读取正确 sheet（`kQHpSt`），并重写报告核心部分。

**根因**：读取飞书数据时未验证用例 ID 格式（应以"对接zentyal-"开头），直接信任了缓存文件。

**改进措施**：读取飞书数据后，立即对第一行和最后一行用例 ID 执行格式断言（正则匹配预期前缀），不通过则拒绝缓存并重新拉取，避免静默使用错误数据。

---

### 7.5 总结

| 问题 | 影响 | 修复成本 | 预防措施 |
|---|---|---|---|
| 打流步骤 ID 遗漏 | 临时打断创建流程 | 低（直接补充） | Phase 0 增加完整步骤链 ID 清单 |
| 步骤结构调整两轮 | 已建 4 条样本废弃重建 | 中（~1h） | Phase 0 明确步骤组成并画 ASCII 示意 |
| 变量名未提前检查 | 批量脚本需分协议处理 | 低（需分支逻辑） | Phase 0 统一 GET 所有公共步骤变量清单 |
| 缓存读错表 | 初版报告整体偏移 | 高（~2h 重写） | 读取后立即断言用例 ID 前缀格式 |
