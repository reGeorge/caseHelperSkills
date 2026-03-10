# 自动化平台操作 Skill

自动化测试平台 API 交互工具，提供用例目录、用例、步骤的完整 CRUD 操作。

## 功能特性

- ✅ 用例目录增删改查
- ✅ 用例增删改查
- ✅ 用例步骤增删改查
- ✅ 变量管理
- ✅ 完整的日志记录

## 配置

在使用前需要设置以下环境变量或配置文件：

```python
TEST_PLATFORM_URL = "https://your-platform.com"  # 平台地址
TEST_PLATFORM_TOKEN = "NDY7d2VpYmluOjE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
CREATOR_NAME = "your_name"
CREATOR_ID = "12345"
DEFAULT_PARENT_ID = 66241  # 默认父目录ID
```

## 使用方法

### 1. 用例目录操作

```python
from platform_client import PlatformClient

client = PlatformClient()

# 创建目录
dir_id = client.create_directory(
    name="测试目录",
    parent_id=66241,
    note="目录描述"
)

# 更新目录
client.update_directory(
    dir_id=66241,
    name="新目录名",
    note="更新后的描述"
)

# 删除目录
client.delete_directory(dir_id=66241)

# 查询目录
dir_info = client.get_directory(dir_id=66241)
sub_dirs = client.list_directories(parent_id=66241)
```

### 2. 用例操作

```python
# 创建用例
case_data = {
    "name": "测试用例名称",
    "description": "用例描述",
    "priority": 2,
    "note": "备注信息"
}

case_id = client.create_case(
    case_data=case_data,
    directory_id=66241
)

# 创建用例（简化API，支持type参数）
case_id = client.create_case(
    name="测试用例名称",
    directory_id=66241,
    description="用例描述",
    note="备注信息",
    priority=2,
    type=1  # 用例类型: 1=个人用例, 默认为自动化用例
)

# 更新用例
client.update_case(
    case_id=66242,
    case_data={
        "name": "更新后的用例名",
        "description": "新描述"
    }
)

# 删除用例
client.delete_case(case_id=66242)

# 查询用例
case_info = client.get_case(case_id=66242)
cases = client.list_cases(directory_id=66241)
```

### 3. 用例步骤操作

```python
# 创建步骤
step_data = {
    "name": "步骤1",
    "order": 1,
    "host": "${G_host}",
    "protocol": 0,  # 0=HTTP
    "path": "/api/test",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": {"key": "value"},
    "check": [{"expect": 200}]
}

step_id = client.create_step(
    case_id=66242,
    step_data=step_data
)

# 更新步骤
client.update_step(
    step_id=step_id,
    step_data={"name": "更新后的步骤名"}
)

# 删除步骤
client.delete_step(step_id=step_id)

# 查询步骤
step_info = client.get_step(step_id)
steps = client.list_steps(case_id=66242)
```

### 4. 变量操作

```python
# 创建变量
var_id = client.create_variable(
    case_id=66242,
    name="变量名",
    value="变量值"
)

# 更新变量
client.update_variable(
    var_id=var_id,
    value="新值"
)

# 删除变量
client.delete_variable(var_id=var_id)

# 查询变量
variables = client.list_variables(case_id=66242)
```

## SDET E2E Case Creation Gotchas & Architecture

在组装端到端 (E2E) 自动化用例时，应严格遵循以下平台架构规范及避免常见错误：

### 1. 必须使用 `caseType: 1` 和 `componentId: 3`
- **错误**：测试用例不可见或不可执行。如果是 `caseType: 0` 会被平台解析为“目录/业务用例”。缺少 `componentId` 会导致平台前端列表里无法展示此用例（例如 SAM+v5 的分类需要 componentId: 3）。
- **正确**：当调用 `/case` 端点创建最终自动化测试用例时，必须传递 `caseType: 1` (或 2 视具体平台配置，当前要求为自动化用例1/2具体按接口) 且必须带有 `componentId: 3`。

### 2. 严格的“搭积木”架构 (Quote Model)
- **错误**：在用例下通过原始 API 配置去生成裸 HTTP 请求步骤。这会破坏平台公用模块的维护性。若调用 `/flow` 时不传 `type` 参数，平台默认会被识别为 `HTTP` (0)。
- **正确**：E2E用例必须由纯**引用步骤 (Quote Steps)** 构成。仅通过向 `/flow` 提交 `quoteId: [public_case_id]` 来拉取已有公共用例，且**必须携带 `"type": 1` 参数**，以此告知平台该步骤属于用例引用而非原生请求。绝不可在自动化用例中直接注入原生的 RADIUS / HTTP 动作。

### 3. 上层变量注入以匹配下层引用 (Variable Overrides)
- **底层强依赖**：引用类似 `66904` (有线1x失败) 等公共用例时，由于它们内部要求 `eap_username`, `eap_password`, `userIP`, `nasIP` 等变量。因此，如果没有给它们传参，在执行时就会报 null 的错误。
- **对应方案**：父级测试用例建立好之后，必须调用 `/case/variable` 接口，显式注入底层引用需要的全部同名变量。这些注入在全局作用域的变量，会自动下沉到各个 quoteId 的步骤中去。

## API 接口说明

### 目录相关接口

- `POST /case` - 创建目录 (caseType=0)
- `PUT /case/{id}` - 更新目录
- `DELETE /case/{id}` - 删除目录
- `GET /case/{id}` - 查询目录
- `GET /case/list` - 查询目录列表

### 用例相关接口

- `POST /case` - 创建用例 (caseType=2)
- `PUT /case/{id}` - 更新用例
- `DELETE /case/{id}` - 删除用例
- `GET /case/{id}` - 查询用例
- `GET /case/list` - 查询用例列表

### 步骤相关接口

- `POST /flow` - 创建步骤
- `PUT /flow/{id}` - 更新步骤
- `DELETE /flow/{id}` - 删除步骤
- `GET /flow/{id}` - 查询步骤
- `GET /flow/list` - 查询步骤列表

### 变量相关接口

- `POST /case/variable` - 创建变量
- `PUT /case/variable/{id}` - 更新变量
- `DELETE /case/variable/{id}` - 删除变量
- `GET /case/variable/list` - 查询变量列表

## 示例

查看 `platform_client.py` 获取完整的实现和示例代码。

## 注意事项

1. 所有接口调用都需要在 header 中携带 token
2. 平台使用自签名证书，代码中已禁用 SSL 警告
3. 创建者和修改者信息会自动注入
4. caseType: 0=目录, 2=自动化用例
5. protocol: 0=HTTP, 1=HTTPS
6. type参数: 1=个人用例, 不传默认为自动化用例

## 环境变量配置

推荐使用环境变量管理配置：

```bash
export SDET_BASE_URL="https://your-platform.com/api/sdet-atp"
export SDET_API_TOKEN="your_token"
export CREATOR_NAME="your_name"
export CREATOR_ID="12345"
```

```python
# 从环境变量读取配置
import os

client = PlatformClient(
    base_url=os.getenv('SDET_BASE_URL'),
    token=os.getenv('SDET_API_TOKEN'),
    creator_name=os.getenv('CREATOR_NAME'),
    creator_id=os.getenv('CREATOR_ID')
)
