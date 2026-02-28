# 自动化平台客户端使用说明

## 配置

在使用前需要获取有效的访问 Token。

### 获取 Token

1. 登录自动化测试平台
2. 进入个人设置或 API 管理页面
3. 生成或复制 API Token

### 环境变量配置

可以在脚本中直接配置，或使用环境变量：

```python
# 方式1: 直接配置
PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"
PLATFORM_TOKEN = "your_token_here"
CREATOR_NAME = "魏斌"
CREATOR_ID = "46"

# 方式2: 使用环境变量
import os
PLATFORM_URL = os.getenv("TEST_PLATFORM_URL", "https://sdet.ruishan.cc/api/sdet-atp")
PLATFORM_TOKEN = os.getenv("TEST_PLATFORM_TOKEN", "")
CREATOR_NAME = os.getenv("TEST_PLATFORM_CREATOR_NAME", "System")
CREATOR_ID = os.getenv("TEST_PLATFORM_CREATOR_ID", "0")
```

### 当前配置信息

- **平台地址**: `https://sdet.ruishan.cc/api/sdet-atp`
- **创建者**: 魏斌 (ID: 46)
- **父目录ID**: 66241
- **测试用例ID**: 66242

## 认证说明

平台使用 Token 进行身份验证，Token 格式为 Base64 编码：

```
原始格式: {用户ID};{用户名}:{时间戳};{密钥}
示例: 46;weibin:1772507480174;3e01130fcafff4d015159dcfba89f99bb4e1432e6770152102e65e8fd6200e21
编码后: NDY7d2VpYmluOjE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==
```

### 认证失败处理

如果遇到 401 认证错误，请检查：

1. **Token 是否有效**
   - Token 是否已过期（检查时间戳）
   - Token 是否被撤销

2. **Token 格式是否正确**
   - 使用 `diagnose_auth.py` 脚本诊断
   - 确认 Token 是 Base64 编码格式

3. **平台访问权限**
   - 确认账号有 API 访问权限
   - 确认 IP 白名单配置

4. **请求格式**
   - Header 必须包含 `token` 字段
   - Header 必须包含 `Content-Type: application/json`

### 诊断工具

运行诊断脚本检查认证问题：

```bash
python skills/sdet-skills/platform-client/diagnose_auth.py
```

## 快速开始

### 1. 基础使用

```python
from platform_client import PlatformClient

# 创建客户端
client = PlatformClient(
    base_url="https://sdet.ruishan.cc/api/sdet-atp",
    token="your_token_here",
    creator_name="魏斌",
    creator_id="46"
)

# 查询用例
result = client.get_case(66242)
if result['success']:
    print(f"用例名称: {result['data']['name']}")
```

### 2. 创建用例

```python
result = client.create_case(
    name="新测试用例",
    directory_id=66241,
    description="用例描述",
    request={
        "method": "POST",
        "url": "/api/test",
        "headers": {"Content-Type": "application/json"},
        "body": {"key": "value"}
    },
    check=[{"expect": 200}]
)

if result['success']:
    print(f"用例创建成功，ID: {result['data']}")
```

### 3. 创建目录

```python
result = client.create_directory(
    name="新测试目录",
    parent_id=66241,
    note="目录描述"
)

if result['success']:
    print(f"目录创建成功，ID: {result['data']}")
```

## API 接口说明

### 目录相关

| 方法 | 接口 | 说明 |
|------|------|------|
| create_directory | POST /case | 创建目录 (caseType=0) |
| update_directory | PUT /case/{id} | 更新目录 |
| delete_directory | DELETE /case/{id} | 删除目录 |
| get_directory | GET /case/{id} | 查询目录 |
| list_directories | GET /case/list | 查询目录列表 |

### 用例相关

| 方法 | 接口 | 说明 |
|------|------|------|
| create_case | POST /case | 创建用例 (caseType=2) |
| update_case | PUT /case/{id} | 更新用例 |
| delete_case | DELETE /case/{id} | 删除用例 |
| get_case | GET /case/{id} | 查询用例 |
| list_cases | GET /case/list | 查询用例列表 |

### 步骤相关

| 方法 | 接口 | 说明 |
|------|------|------|
| create_step | POST /flow | 创建步骤 |
| update_step | PUT /flow/{id} | 更新步骤 |
| delete_step | DELETE /flow/{id} | 删除步骤 |
| get_step | GET /flow/{id} | 查询步骤 |
| list_steps | GET /flow/list | 查询步骤列表 |

### 变量相关

| 方法 | 接口 | 说明 |
|------|------|------|
| create_variable | POST /case/variable | 创建变量 |
| update_variable | PUT /case/variable/{id} | 更新变量 |
| delete_variable | DELETE /case/variable/{id} | 删除变量 |
| list_variables | GET /case/variable/list | 查询变量列表 |

## 测试脚本

### 运行完整测试

```bash
python skills/sdet-skills/platform-client/test_operations.py
```

### 运行示例

```bash
python skills/sdet-skills/platform-client/example.py
```

### 认证诊断

```bash
python skills/sdet-skills/platform-client/diagnose_auth.py
```

## 注意事项

1. **SSL 证书**: 平台使用自签名证书，代码中已禁用 SSL 验证
2. **Token 安全**: 请妥善保管 Token，不要提交到版本控制系统
3. **批量操作**: 避免在短时间内发送大量请求，可能触发限流
4. **错误处理**: 所有方法都返回统一格式 `{"success": bool, "data": any, "message": str}`
5. **日志记录**: 可以在调用方法前添加日志记录，方便调试

## 故障排除

### 401 Unauthorized

- 检查 Token 是否有效
- 运行 `diagnose_auth.py` 诊断
- 联系平台管理员重新生成 Token

### 403 Forbidden

- 检查账号权限
- 确认 IP 白名单设置

### 404 Not Found

- 检查资源 ID 是否正确
- 确认资源是否存在

### 500 Server Error

- 联系平台管理员
- 检查请求参数格式

## 联系支持

如遇到问题，请联系：
- 平台管理员
- 开发团队

## 更新日志

- 2026-02-28: 初始版本，支持目录/用例/步骤/变量的完整 CRUD 操作
