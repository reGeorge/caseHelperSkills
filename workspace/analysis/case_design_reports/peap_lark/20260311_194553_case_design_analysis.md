# 用例设计分析报告 v2

> 生成时间: 2026-03-11 19:45:53 | 用例: 61 | 维度: 0 | 业务动作: 12 | 不可自动化: 0 | 缺后端验证: 5

---

## §1 业务动作聚类

> 碎片UI步骤 → 业务动作，每个业务动作对应一个公共步骤的粒度。

| 动作ID | 业务动作 | 意图链 | 覆盖用例 | 数据注入点 | 可自动化 |
|--------|---------|--------|---------|-----------|----------|
| BA_000 | 组合操作(OTHER→EXECUTE) | `EXECUTE→OTHER→EXECUTE` | 35 | — | ✅ |
| BA_001 | 组合操作(OTHER→EXECUTE) | `EXECUTE→OTHER→OTHER→OTHER` | 8 | — | ✅ |
| BA_002 | 组合操作(OTHER→EXECUTE) | `EXECUTE→OTHER→OTHER→EXECUTE` | 4 | — | ✅ |
| BA_003 | 组合操作(INPUT→EXECUTE) | `EXECUTE→INPUT` | 4 | 错误密码 | ✅ |
| BA_004 | 组合操作(OTHER→EXECUTE) | `EXECUTE→OTHER→OTHER→OTHER→OTHER→OTHER` | 2 | — | ✅ |
| BA_005 | 组合操作(INPUT→EXECUTE) | `EXECUTE→INPUT→INPUT` | 2 | LDAP账户的密码, 本地账户的密码 | ✅ |
| BA_006 | 组合操作(OTHER→EXECUTE) | `EXECUTE→OTHER` | 1 | — | ✅ |
| BA_007 | 组合操作(OTHER→INPUT→EXECUTE→SELECT) | `SELECT→OTHER→OTHER→INPUT→EXECUTE` | 1 | 证书密码 | ✅ |
| BA_008 | 组合操作(SELECT) | `SELECT→SELECT` | 1 | — | ✅ |
| BA_009 | 组合操作(OTHER→INPUT→EXECUTE) | `OTHER→INPUT→EXECUTE` | 1 | 证书密码 | ✅ |
| BA_010 | 组合操作(EXECUTE) | `EXECUTE` | 1 | — | ✅ |
| BA_011 | 组合操作(INPUT→EXECUTE) | `INPUT→EXECUTE` | 1 | — | ✅ |

### 建议公共步骤清单

**可建公共步骤**:

- `【公共】组合操作(OTHER→EXECUTE)`
  - 原始步骤: 使用win10电脑连接1x信号 → 使用本地用户进行认证 → 终端断开信号
- `【公共】组合操作(OTHER→EXECUTE)`
  - 原始步骤: 使用win10电脑连接1x信号 → 认证源使用默认配置 → 使用本地用户进行认证
- `【公共】组合操作(OTHER→EXECUTE)`
  - 原始步骤: 使用win10电脑连接1x信号 → 认证源使用默认配置 → 使用本地用户进行认证
- `【公共】组合操作(INPUT→EXECUTE)（{错误密码}）`
  - 原始步骤: 使用win10电脑连接1x信号 → 使用LDAP用户进行认证，输入错误密码
  - 参数化变量: `错误密码`
- `【公共】组合操作(OTHER→EXECUTE)`
  - 原始步骤: 使用win10电脑连接1x信号 → 认证源使用默认配置 → 使用LDAP用户进行认证
- `【公共】组合操作(INPUT→EXECUTE)（{LDAP账户的密码}, {本地账户的密码}）`
  - 原始步骤: 使用win10电脑连接1x信号 → 使用账户名相同的用户进行认证，输入LDAP账户的密码 → 使用账户名相同的用户进行认证，输入本地账户的密码
  - 参数化变量: `LDAP账户的密码`, `本地账户的密码`
- `【公共】组合操作(OTHER→EXECUTE)`
  - 原始步骤: 使用win10电脑连接1x信号 → 使用LDAP用户进行认证
- `【公共】组合操作(OTHER→INPUT→EXECUTE→SELECT)（{证书密码}）`
  - 原始步骤: 上传1x认证证书，选择非pfx 和pem格式文件 → 上传大于10MB的证书文件 → 上传小于10MB的1x证书
  - 参数化变量: `证书密码`
- `【公共】组合操作(SELECT)`
  - 原始步骤: 进行点击上传1x证书，选择对应证书文件 → 进行拖拽上传1x证书，选择对应证书文件
- `【公共】组合操作(OTHER→INPUT→EXECUTE)（{证书密码}）`
  - 原始步骤: 上传1x证书 → 输入证书密码 → 点击保存
  - 参数化变量: `证书密码`
- `【公共】组合操作(EXECUTE)`
  - 原始步骤: 鼠标悬停或点击 1x认证默认协议 右侧帮助说明
- `【公共】组合操作(INPUT→EXECUTE)`
  - 原始步骤: 修改1x认证默认认证协议为EAP-TTLS → 点击保存

## §2 维度归纳

> ⚠️ 未归纳出多值维度，建议在用例前置条件中明确写出关键参数。

## §3 笛卡尔积缺口

> **复盘§1.2**: 3个开关 → 2³=8种组合，只建3个公共步骤 → 37/80用例引用错误。

**组合总数**: 0 | **已覆盖**: 0 | **缺失**: 0

✅ 所有维度组合均有对应用例覆盖

## §4 API对齐 + 类型陷阱

### config_rules 状态覆盖

- 规则维度: 首次登录强制修改, 弱密码强制处理, 定时强制修改, 提前短信通知
- 应有组合: 16 | 已有: 4 （步骤: 66888, 66889, 66890, 66891）
- ⚠️ **缺失组合 12 个**:
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'False', '定时强制修改': 'True', '提前短信通知': 'False'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'False', '定时强制修改': 'False', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'False', '定时强制修改': 'True', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'True', '定时强制修改': 'False', '提前短信通知': 'False'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'True', '定时强制修改': 'False', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'False', '定时强制修改': 'True', '提前短信通知': 'False'}
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'True', '定时强制修改': 'False', '提前短信通知': 'False'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'False', '定时强制修改': 'True', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'False', '定时强制修改': 'False', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'False', '弱密码强制处理': 'True', '定时强制修改': 'True', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'True', '定时强制修改': 'False', '提前短信通知': 'True'}
  - {'首次登录强制修改': 'True', '弱密码强制处理': 'True', '定时强制修改': 'True', '提前短信通知': 'False'}

### 🔴 类型陷阱（来自复盘）

| # | 陷阱 | 来源 |
|---|------|------|
| 1 | method字段必须传 int(0=GET/1=POST/2=PUT/3=DELETE)，不能传字符串 'POST' | §2.1 |
| 2 | 更新操作必须走 GET→改→POST集合端点，平台不支持直接PUT | §2.2 |
| 3 | body字段传 dict 即可，由 platform_client 内部做一次 json.dumps，禁止调用方再序列化 | §2.3 |
| 4 | 从JSON/API读入的ID做dict lookup前，必须统一转str：mapping.get(str(quote_id)) | §2.4 |

## §5 双重验证方案

> 每条用例的「预期结果」分解为: **前端表现**（UI断言）+ **后端真相**（API/Log断言）
> 缺少后端验证的用例: **5/61**

| 用例ID | 前端表现 | 后端真相 | 缺后端 |
|--------|---------|---------|-------|
| PEAP-001 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-002 | [UI_GENERAL] 用户不存在 | [API_AUTH_REJECT] 认证失败 | ✅ |
| PEAP-003 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-004 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-005 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-006 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-007 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-008 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-009 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-010 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-011 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-012 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-013 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-014 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-015 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-016 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-017 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-018 | — | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态; [API_AUTH_RESULT | ✅ |
| PEAP-019 | — | [API_AUTH_REJECT] 认证失败 | ✅ |
| PEAP-020 | [UI_GENERAL] 用户不存在 | [API_AUTH_REJECT] 认证失败 | ✅ |
| PEAP-021 | — | [API_AUTH_RESULT] 2.认证失败
3.认证成功 | ✅ |
| PEAP-022 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-023 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端不断开信号仍是在线状态; [UI_GENERA | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-024 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-025 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-026 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-027 | [UI_GENERAL] 用户信息和终端信息正确
6.用户及终端为离线状态 | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态 | ✅ |
| PEAP-028 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-029 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-030 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-031 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-032 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-033 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-034 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-035 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-036 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-037 | — | [API_AUTH_RESULT] 3.认证成功
4.用户及终端为在线状态; [API_AUTH_RESULT | ✅ |
| PEAP-038 | — | [API_AUTH_REJECT] 认证失败 | ✅ |
| PEAP-039 | [UI_GENERAL] 用户不存在 | [API_AUTH_REJECT] 认证失败 | ✅ |
| PEAP-040 | — | [API_AUTH_RESULT] 2.认证失败
3.认证成功 | ✅ |
| PEAP-041 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-042 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-043 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-044 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-045 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-046 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-047 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-048 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-049 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-050 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-051 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-052 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-053 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-054 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-055 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-056 | [UI_GENERAL] 用户信息和终端信息正确
5.用户及终端为离线状态 | [API_AUTH_RESULT] 2.认证成功
3.用户及终端为在线状态 | ✅ |
| PEAP-057 | [UI_TOAST] 1.提示文件格式错误
2.提示文件大小超出限制
3.上传成功
5.弹出“注意”弹窗：“更 | — | 🔴 **是** |
| PEAP-058 | [UI_GENERAL] 两种方式均可上传证书 | — | 🔴 **是** |
| PEAP-059 | [UI_GENERAL] 1.上传成功
3.保存成功
4.待服务重启完成后可以看到证书详情包含“生效时间”;  | — | 🔴 **是** |
| PEAP-060 | [UI_GENERAL] 帮助说明文本为：当客户端发起基于EAP协议的1x认证时; [UI_GENERAL]  | — | 🔴 **是** |
| PEAP-061 | [UI_GENERAL] 1.默认 1x认证默认协议为 PEAP
2.不可修改为空
3.点击保存后有“注意”弹 | — | 🔴 **是** |

### 缺少后端验证的用例，建议补充以下断言类型:

- `API_AUTH_RESULT` — 调用 GET /auth/status 断言认证状态
- `API_ONLINE_DEVICE` — 调用 GET /device/online 断言设备在线列表
- `LOG_CHECK` — 查询日志接口，断言日志中含关键字

## §6 风险与不可自动化标注

✅ 未发现不可自动化风险

## §7 复盘防护检查

> 逐条对应 `knowledge/case_design/insight.md` 的血泪教训

| # | 检查项 | 来源 | 本报告覆盖情况 |
|---|--------|------|---------------|
| 1 | Phase 0 先输出状态组合映射表再动手 | §1.1 | ✅ §3已输出笛卡尔积矩阵，缺口0个 |
| 2 | 公共步骤颗粒度 = 独立维度全排列 | §1.2 | ✅ 0个维度，全排列已计算 |
| 3 | 先单条验证API参数再批量 | §1.3 | ⚠️ 请在执行前手工验证一条 create_step |
| 4 | 审计前置，非事后补救 | §1.4 | ✅ 本报告即 Phase 0 前置分析 |
| 5 | method 字段传 int(0/1/2/3) | §2.1 | ✅ §4类型陷阱已列出 |
| 6 | 更新走 GET→改→POST | §2.2 | ✅ §4类型陷阱已列出 |
| 7 | body 不要双重序列化 | §2.3 | ✅ §4类型陷阱已列出 |
| 8 | dict key int/str 一致 | §2.4 | ✅ §4类型陷阱已列出 |
| 9 | 公共步骤 body 从模板派生 | §2.6 | ⚠️ 请从已验证用例 GET 原始 body 后派生 |

## §8 实施路线图

**Phase 1 — 补齐公共步骤** (0 个缺口)
1. 从已验证 body 模板派生各缺口的 HTTP body
2. 单条 create_step API 验证参数正确性
3. 批量创建全部缺失公共步骤

**Phase 2 — 样本创建+审计**
1. 每种组合创建 1 条样本业务用例
2. 用 case-debugger 审计：CONFIG_MISMATCH = 0 才继续

**Phase 3 — 批量+全量审计**
1. 批量创建剩余业务用例
2. 全量审计，所有偏差类型均为 0
3. 同步 case_id 到飞书，更新知识库 manifest

