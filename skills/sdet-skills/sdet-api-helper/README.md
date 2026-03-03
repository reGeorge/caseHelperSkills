# SDET API Helper Skill

## 功能概述

提供SDET自动化测试平台的API对接能力，支持用例、步骤、变量的增删改查以及用例执行。

## 核心能力

### 1. 查询操作

#### 1.1 查询用例详情
```python
get_case_detail(case_id, use_v2=True)
```
- **参数**:
  - `case_id`: 用例ID
  - `use_v2`: 是否使用v2版本接口（默认True）
- **返回**: 用例详情数据

#### 1.2 查询步骤列表
```python
get_case_flows(case_id)
```
- **参数**: `case_id` - 用例ID
- **返回**: 步骤列表

#### 1.3 查询变量列表
```python
get_case_variables(case_id)
```
- **参数**: `case_id` - 用例ID
- **返回**: 变量列表

#### 1.4 查询用例列表
```python
get_case_list(parent_id, case_type=2)
```
- **参数**:
  - `parent_id`: 父目录ID
  - `case_type`: 用例类型（2=自动化用例，0=目录）
- **返回**: 用例列表

#### 1.5 查询步骤详情
```python
get_flow_detail(flow_id)
```
- **参数**: `flow_id` - 步骤ID
- **返回**: 步骤详情

### 2. 执行操作

#### 2.1 触发用例调试
```python
trigger_case_debug(case_id, env_id=93, flow_ids=None)
```
- **参数**:
  - `case_id`: 用例ID
  - `env_id`: 环境ID（默认93）
  - `flow_ids`: 指定执行的步骤ID列表（None表示执行全部）
- **返回**: 执行日志ID

#### 2.2 查询执行结果
```python
get_debug_logs(log_id)
```
- **参数**: `log_id` - 执行日志ID
- **返回**: 执行结果详情
- **注意**: 需要在触发执行后等待一段时间再查询

### 3. 创建操作

#### 3.1 创建目录
```python
ensure_test_directory(name, parent_id=None)
```
- **参数**:
  - `name`: 目录名称
  - `parent_id`: 父目录ID（None则使用默认配置）
- **返回**: 目录ID

#### 3.2 创建用例
```python
sync_case_to_platform(case_info, directory_id)
```
- **参数**:
  - `case_info`: 用例信息字典
  - `directory_id`: 目录ID
- **返回**: `{"id": case_id, "status": "success/failed"}`

#### 3.3 创建步骤（支持公共步骤引用）
```python
create_flow(case_id, flow_data)
```
- **参数**:
  - `case_id`: 用例ID
  - `flow_data`: 步骤数据
    - **普通HTTP步骤** (type=0):
      ```python
      {
          "type": 0,
          "name": "步骤名称",
          "host": "${G_host}",
          "port": "${G_port}",
          "path": "/api/test",
          "method": "POST",
          "headers": [{"key": "Content-Type", "value": "application/json"}],
          "body": "{}",
          "check": [
              {
                  "expression": "$.code",
                  "expectValue": "0",
                  "operator": 0
              }
          ]
      }
      ```
    - **公共步骤引用** (type=1):
      ```python
      {
          "type": 1,
          "quoteId": "55635",  # 被引用的公共步骤ID
          "name": "步骤名称",
          "exception": 0,
          "delayTime": 0
      }
      ```
- **返回**: 步骤ID

#### 3.4 创建变量
在创建用例时自动处理，或手动调用内部方法：
```python
# 变量会自动在 sync_case_to_platform 中创建
# case_info 中包含 "variables" 字段：
{
    "variables": [
        {"name": "username", "value": "test001"},
        {"name": "password", "value": "123456"}
    ]
}
```

## 使用示例

### 示例1: 学习现有用例

```python
# 1. 查询用例详情
case_detail = get_case_detail(65633)

# 2. 查询步骤列表
flows = get_case_flows(65633)

# 3. 分析公共步骤引用
for flow in flows:
    if flow.get("type") == 1:
        print(f"公共步骤引用: {flow['name']} -> quoteId: {flow['quoteId']}")

# 4. 查询变量列表
variables = get_case_variables(65633)
```

### 示例2: 执行用例并查看结果

```python
# 1. 触发用例调试
log_id = trigger_case_debug(65633, env_id=93)

# 2. 等待执行完成（建议等待10秒以上）
import time
time.sleep(10)

# 3. 查询执行结果
result = get_debug_logs(log_id)
print(f"执行状态: {result.get('status')}")
```

### 示例3: 创建新用例

```python
# 1. 创建目录
dir_id = ensure_test_directory("测试目录")

# 2. 准备用例数据
case_info = {
    "name": "测试用例名称",
    "priority": 2,
    "description": "用例描述",
    "variables": [
        {"name": "userIP", "value": "5.1.1.2"},
        {"name": "userMac", "value": "525400541900"}
    ],
    "request": {
        "method": "POST",
        "url": "/api/test",
        "headers": {"Content-Type": "application/json"},
        "body": {"username": "${userIP}"}
    },
    "check": [
        {
            "expression": "$.code",
            "expectValue": "0",
            "operator": 0
        }
    ]
}

# 3. 创建用例（会自动创建变量和步骤）
result = sync_case_to_platform(case_info, dir_id)
```

## 公共步骤引用机制

### 什么是公共步骤？
公共步骤是封装好的可复用测试步骤，如登录、清理数据、认证流程等。

### 如何识别公共步骤？
在步骤数据中：
- `type=1` 表示这是公共步骤引用
- `quoteId` 指向被引用的公共步骤ID

### 公共步骤的优势
1. **复用性**: 多个用例可以引用同一个公共步骤
2. **可维护性**: 修改公共步骤后，所有引用该步骤的用例自动更新
3. **可读性**: 用例步骤更清晰，聚焦业务逻辑

### 常见公共步骤
- 登录鉴权类（如：UNC管理端登录）
- 数据清理类（如：删除无感认证记录）
- 认证流程类（如：有线web认证全流程）

## 变量机制

### 全局变量 vs 用例变量
- **全局变量**: `${G_host}`, `${G_port}` 等，在环境中配置
- **用例变量**: 在用例中定义，仅当前用例可用

### 变量引用方式
使用 `${变量名}` 格式引用变量

### 变量使用场景
- 请求参数参数化
- 断言值动态化
- 数据驱动测试

## 接口路径对照表

| 操作类型 | 接口路径 | 说明 |
|---------|---------|------|
| 查询用例详情(v2) | `/case/v2/{caseId}` | 获取用例详细信息 |
| 查询步骤列表 | `/flows/{caseId}` | 获取用例所有步骤 |
| 查询变量列表 | `/case/variables/{caseId}` | 获取用例所有变量 |
| 查询用例列表 | `/case/list?parent={parentId}&caseType={type}` | 查询指定目录下的用例 |
| 查询步骤详情 | `/flow/{flowId}` | 获取单个步骤详情 |
| 触发调试 | `/case/debug` | 触发用例执行 |
| 查询执行结果 | `/case/debug/logs/{logId}` | 获取执行日志 |
| 创建目录/用例 | `/case` | POST请求创建 |
| 创建步骤 | `/flow` | POST请求创建 |
| 创建变量 | `/case/variable` | POST请求创建 |

## 配置说明

在 `config.py` 中需要配置：
- `TEST_PLATFORM_URL`: 平台基础URL
- `TEST_PLATFORM_TOKEN`: 认证token
- `CREATOR_NAME`: 创建者名称
- `CREATOR_ID`: 创建者ID
- `DEFAULT_PARENT_ID`: 默认父目录ID
