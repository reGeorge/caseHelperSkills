# SDET平台登录工具

## 功能说明

处理SDET平台401鉴权失效场景，通过账号密码登录获取新的token。

## 使用场景

- 调用SDET API时遇到401 Unauthorized错误
- Token过期需要重新获取
- 首次使用SDET平台时获取token

## API接口

### SDETLogin类

#### 初始化

```python
from sdet_login import SDETLogin

login = SDETLogin()
```

#### 主要方法

##### login(username, password)

使用账号密码登录SDET平台，返回token。

```python
result = login.login("weibin", "Wb@13011235")

if result['success']:
    print(f"登录成功！Token: {result['token']}")
    print(f"用户信息: {result['user_info']}")
else:
    print(f"登录失败: {result['error']}")
```

##### save_token_to_config(token)

将token保存到config.yaml配置文件。

```python
login.save_token_to_config(result['token'])
print("Token已保存到配置文件")
```

## 使用示例

### 示例1: 基本登录流程

```python
from sdet_login import SDETLogin

login = SDETLogin()

# 登录获取token
result = login.login("your_username", "your_password")

if result['success']:
    print(f"登录成功！")
    print(f"Token: {result['token']}")
    print(f"用户: {result['user_info']['username']}")
    
    # 保存token到配置文件
    login.save_token_to_config(result['token'])
else:
    print(f"登录失败: {result['error']}")
```

### 示例2: 自动刷新token

```python
import os
from sdet_login import SDETLogin

# 检查当前token是否有效
token = os.getenv('SDET_API_TOKEN')

# 如果token无效(401错误),重新登录
login = SDETLogin()
result = login.login("weibin", "Wb@13011235")

if result['success']:
    # 更新环境变量
    os.environ['SDET_API_TOKEN'] = result['token']
    print("Token已更新")
```

### 示例3: 交互式获取token

```python
from sdet_login import SDETLogin

login = SDETLogin()

# 通过用户输入获取账号密码
username = input("请输入SDET平台用户名: ")
password = input("请输入密码: ")

result = login.login(username, password)

if result['success']:
    login.save_token_to_config(result['token'])
    print("登录成功！Token已保存到配置文件")
else:
    print(f"登录失败: {result['error']}")
```

## 错误处理

### 常见错误

1. **用户名或密码错误**
   - 错误码: 401
   - 解决: 检查账号密码是否正确

2. **网络连接失败**
   - 错误: ConnectionError
   - 解决: 检查网络连接

3. **服务器错误**
   - 错误码: 500
   - 解决: 稍后重试

### 错误处理示例

```python
from sdet_login import SDETLogin

login = SDETLogin()
result = login.login("username", "password")

if not result['success']:
    error_code = result.get('error_code')
    error_msg = result.get('error')
    
    if error_code == 401:
        print("用户名或密码错误，请重新输入")
    elif 'ConnectionError' in error_msg:
        print("网络连接失败，请检查网络")
    else:
        print(f"登录失败: {error_msg}")
```

## 返回数据格式

### 成功响应

```python
{
    'success': True,
    'token': 'NDY7d2VpYmluOjE3NzI1MDc0ODAxNzQ7...',
    'user_info': {
        'id': 46,
        'username': 'weibin',
        'name': '魏斌',
        'email': 'weibin@example.com'
    },
    'message': '登录成功'
}
```

### 失败响应

```python
{
    'success': False,
    'error': '用户名或密码错误',
    'error_code': 401
}
```

## API端点

- **登录接口**: `POST https://sdet.ruishan.cc/api/sdet-base/user/login`
- **请求体**: `{"code": "用户名", "key": "密码"}`
- **返回体**: `{"code": 0, "data": {"token": "...", "user": {...}}}`

## 配置文件

登录成功后，token会自动保存到 `agent_service/config.yaml`:

```yaml
secrets:
  SDET_API_TOKEN: "NDY7d2VpYmluOjE3NzI1MDc0ODAxNzQ7..."
```

## 安全建议

1. **不要硬编码密码**: 账号密码应通过环境变量或用户输入获取
2. **定期更新token**: Token会过期，建议定期刷新
3. **保护配置文件**: config.yaml包含敏感信息，不要提交到git

## 依赖

- requests: HTTP请求
- json: JSON处理
- yaml: 配置文件读写

## 版本历史

- v1.0.0 (2026-03-03): 初始版本
  - 支持账号密码登录
  - 自动保存token到配置文件
  - 完整的错误处理
