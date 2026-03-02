# 飞书Access Token获取器

这个skill帮助用户获取飞书API的access_token，用于后续的API调用。

## 功能说明

- 使用飞书应用的app_id和app_secret获取access_token
- 自动处理API请求和错误处理
- 提供清晰的输出结果

## 使用场景

当用户需要：
- 访问飞书API时
- 获取access_token用于其他飞书API调用
- 测试飞书应用凭证是否有效

## 使用方法

1. 确保已安装requests库：`pip install requests`
2. 配置app_id和app_secret
3. 运行脚本获取access_token

## 参数说明

- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥

## API端点

```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

## 返回结果

成功时返回：
- access_token字符串
- 有效期信息

失败时返回：
- 错误信息
- 错误码

## 注意事项

- access_token有有效期，过期后需要重新获取
- 请妥善保管app_secret和access_token
- 确保应用已开通相应权限
