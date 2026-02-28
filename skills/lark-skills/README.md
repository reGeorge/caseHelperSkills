# 飞书API Skills

这个目录包含了用于与飞书API交互的skills。

## Skills列表

### 1. lark-access-token
**功能**: 获取飞书API的access_token

**使用场景**:
- 需要访问飞书API时
- 获取access_token用于其他飞书API调用
- 测试飞书应用凭证是否有效

**文件**:
- `SKILL.md`: Skill说明文档
- `lark_access_token.py`: Python脚本

**使用方法**:
```bash
cd skills/lark-access-token
python lark_access_token.py
```

### 2. lark-sheets
**功能**: 获取飞书表格的所有工作表列表

**使用场景**:
- 查看飞书表格中有哪些工作表
- 获取特定工作表的ID
- 了解表格结构

**文件**:
- `SKILL.md`: Skill说明文档
- `lark_sheets.py`: Python脚本

**使用方法**:
```bash
cd skills/lark-sheets
python lark_sheets.py
```

### 3. lark-api-helper
**功能**: 飞书API综合助手，提供access_token获取、表格操作等功能

**使用场景**:
- 访问飞书API进行任何操作
- 管理飞书表格数据
- 获取飞书资源信息
- 自动化飞书工作流程

**文件**:
- `SKILL.md`: Skill说明文档
- `lark_access_token.py`: Access Token获取脚本
- `lark_sheets.py`: 表格操作脚本

**使用方法**:
```bash
cd skills/lark-api-helper

# 获取access_token
python lark_access_token.py

# 获取工作表列表
python lark_sheets.py
```

## 依赖要求

所有skills都需要以下Python库：
```bash
pip install requests
```

## 配置说明

### 必需配置
- `app_id`: 飞书应用ID
- `app_secret`: 飞书应用密钥

### 可选配置
- `spreadsheet_token`: 表格token（用于表格操作）
- `access_token`: 访问令牌（可以通过lark-access-token获取）

## 权限要求

确保飞书应用已开通以下权限：
- `sheets:spreadsheet`: 表格访问权限
- `sheets:spreadsheet.readonly`: 只读权限（如需要）
- `sheets:spreadsheet.readwrite`: 读写权限（如需要）

## 使用流程

1. **获取Access Token**
   - 使用lark-access-token或lark-api-helper获取token
   - 保存token供后续使用

2. **操作表格**
   - 使用lark-sheets或lark-api-helper获取工作表列表
   - 根据sheet_id进行具体操作

3. **数据处理**
   - 读取/写入数据
   - 更新记录
   - 查询数据

## 注意事项

- access_token有有效期，通常为2小时
- 请妥善保管app_secret和access_token
- 遵守飞书API调用频率限制
- 确保网络连接稳定

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

## API端点

### 认证
```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/
```

### 表格
```
GET https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
```

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
