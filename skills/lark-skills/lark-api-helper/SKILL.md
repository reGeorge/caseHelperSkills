---
name: "lark-api-helper"
description: "飞书API综合助手，提供access_token获取、表格操作等功能。Invoke when user needs to work with Feishu/Lark APIs or requests any Lark/Feishu operations."
---

# 飞书API综合助手

这个skill提供飞书API的完整操作支持，包括认证、表格操作等功能。

## 功能模块

### 1. Access Token获取
- 使用app_id和app_secret获取access_token
- 自动处理token有效期
- 支持token刷新

### 2. 表格操作
- 获取工作表列表
- 读取表格数据
- 写入表格数据
- 更新表格数据

### 3. 错误处理
- 完善的异常处理机制
- 详细的错误信息输出
- 自动重试机制

## 使用场景

当用户需要：
- 访问飞书API进行任何操作
- 管理飞书表格数据
- 获取飞书资源信息
- 自动化飞书工作流程

## 使用流程

1. **获取Access Token**
   - 使用lark-access-token获取token
   - 保存token供后续使用

2. **操作表格**
   - 使用lark-sheets获取工作表列表
   - 根据sheet_id进行具体操作

3. **数据处理**
   - 读取/写入数据
   - 更新记录
   - 查询数据

## 配置要求

### 必需配置
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥

### 可选配置
- `spreadsheet_token`: 表格token
- `sheet_id`: 工作表ID
- `access_token`: 访问令牌

## API端点汇总

### 认证
```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

### 表格
```
GET https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
```

## 权限要求

确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readonly`: 只读权限（如需要）
- `sheets:spreadsheet.readwrite`: 读写权限（如需要）

## 最佳实践

1. **Token管理**
   - 定期刷新access_token
   - 不要硬编码token到代码中
   - 使用环境变量存储敏感信息

2. **错误处理**
   - 检查API响应状态码
   - 处理网络异常
   - 记录错误日志

3. **性能优化**
   - 合理使用缓存
   - 批量操作减少API调用
   - 处理分页数据

## 示例用法

### 获取工作表列表
```python
# 使用lark-sheets skill
spreadsheet_token = "your_token"
access_token = "your_access_token"
# 调用API获取工作表列表
```

### 读取数据
```python
# 使用sheet_id读取特定工作表数据
sheet_id = "your_sheet_id"
# 调用API读取数据
```

## 注意事项

- access_token有有效期，通常为2小时
- 请妥善保管app_secret和access_token
- 遵守飞书API调用频率限制
- 确保网络连接稳定
- 处理API返回的错误信息

## 故障排除

### 常见问题

1. **401 Unauthorized**
   - 检查access_token是否有效
   - 检查token是否过期

2. **403 Forbidden**
   - 检查应用权限设置
   - 确认资源访问权限

3. **404 Not Found**
   - 检查spreadsheet_token是否正确
   - 确认表格存在

4. **429 Too Many Requests**
   - 减少API调用频率
   - 实现请求限流
