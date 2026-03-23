# 公共步骤创建引导

**创建时间**: 2026-03-18  
**任务**: 多业务服务公共步骤建设

---

## 📋 已有公共步骤清单

从 `knowledge/common_cases_manifest.json` 查询到的相关公共步骤:

### 业务服务相关

| 步骤名称 | step_id | 相关性 |
|---------|:--------:|--------|
| 【常用】 在root用户组下创建指定名称的用户组 | 56508 | ⚠️ 用户组管理,非业务服务 |
| 【常用】 在root用户组下创建指定模板、套餐的用户组 | 65291 | ⚠️ 用户组管理,非业务服务 |
| 【常用】 创建指定名称的模板 | 65295 | ⚠️ 模板管理,非业务服务 |
| 【常用】 创建指定名称的用户模板、套餐、并更新套餐规则的接入控制 | 65298 | ⚠️ 模板管理,非业务服务 |
| 【常用】 更新套餐 | 65867 | ⚠️ 套餐管理,非业务服务 |
| 【常用】 查询用户并充值缴费 | 51426 | ⚠️ 计费功能,非业务服务 |

### 认证相关

| 步骤名称 | step_id | 相关性 |
|---------|:--------:|--------|
| 【常用】 指定用户开户+有线1x认证+记账+查询在线设备（不下线账号） | 51418 | ⚠️ 认证流程,非业务服务管理 |

---

## 🔍 分析结论

### 当前现状
❌ **无直接可复用的业务服务公共步骤**  
现有manifest中没有直接对应业务服务管理的公共步骤。

### 原因分析
1. **业务差异**: 多业务服务功能可能是一个新的业务场景
2. **步骤定位**: 现有步骤主要集中在认证、接入控制、计费等基础功能
3. **功能域**: 业务服务管理可能属于独立的业务模块

---

## 📝 待创建公共步骤清单

基于Phase 0分析,以下6个公共步骤需要新建:

### 1. 【公共】登录管理端

**step_id**: 待创建  
**关键特性**:
- 功能: 登录SAM管理后台
- 输入: 管理员账号(admin)、密码
- 输出: session_token / user_info
- 类型: 认证类步骤

**API契约**:
```
POST /api/login
Request:
{
  "username": "admin",
  "password": "admin_password"
}
Response:
{
  "code": 0,
  "data": {
    "token": "xxx",
    "userInfo": {...}
  }
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| admin_username | string | admin | ✅ | 管理员用户名 |
| admin_password | string | password | ✅ | 管理员密码 |

**测试数据**:
- 正常账号: admin/password
- 错误账号: wrong/pass
- 空账号: ""/password

---

### 2. 【公共】开通上网服务用户

**step_id**: 待创建  
**关键特性**:
- 功能: 创建新的上网认证用户
- 输入: 用户名、密码、模板套餐
- 输出: 用户ID、用户信息
- 类型: 创建类步骤

**API契约**:
```
POST /api/users/create
Request:
{
  "username": "zhangsan",
  "password": "shyfzx@163",
  "templateId": "default_template",
  "userGroup": "root"
}
Response:
{
  "code": 0,
  "data": {
    "userId": 1001,
    "username": "zhangsan",
    "status": "normal"
  }
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| username | string | zhangsan | ✅ | 上网用户名 |
| password | string | pass123 | ✅ | 用户密码 |
| template | string | 默认模板 | ✅ | 用户套餐模板 |
| userGroup | string | root | ⚠️ | 用户组(通常固定) |

**测试数据**:
- 正常创建: zhangsan/pass123/默认模板
- 重复用户: zhangsan/pass123/默认模板(预期失败)
- 密码为空: zhangsan/"/默认模板(预期失败)

---

### 3. 【公共】新增业务服务用户

**step_id**: 待创建  
**关键特性**:
- 功能: 为上网用户开通业务服务
- 输入: service_type(打印机/IP/邮箱)、业务服务用户名、密码、模板
- 输出: 业务服务用户ID
- 类型: 创建类步骤

**API契约**:
```
POST /api/business-service/users/create
Request:
{
  "internetUserId": 1001,
  "serviceType": "printer",
  "serviceUsername": "Pr_zhangsan",
  "password": "pass123",
  "templateId": "printer_template"
}
Response:
{
  "code": 0,
  "data": {
    "serviceUserId": 2001,
    "serviceUsername": "Pr_zhangsan",
    "status": "normal"
  }
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| internetUserId | number | 1001 | ✅ | 上网用户ID |
| serviceType | string | 打印机 | ✅ | 业务服务类型(打印机/IP/邮箱) |
| serviceUsername | string | Pr_zhangsan | ✅ | 业务服务用户名 |
| password | string | pass123 | ✅ | 业务服务密码 |
| templateId | string | 默认模板 | ✅ | 套餐模板 |

**服务类型枚举**:
- 打印机
- IP
- 邮箱

**测试数据**:
- 打印机服务: 1001/打印机/Pr_zhangsan/pass123
- IP服务: 1001/IP/Ip_202118066005/pass123
- 邮箱服务: 1001/邮箱/Em_zhangsan_1/pass123
- 数量超限: 同一用户开通第4个服务(预期失败)

---

### 4. 【公共】删除业务服务用户

**step_id**: 待创建  
**关键特性**:
- 功能: 删除指定的业务服务用户
- 输入: 业务服务用户名或ID
- 输出: 删除结果
- 类型: 删除类步骤
- 前置条件: 需检查该用户是否关联其他业务

**API契约**:
```
DELETE /api/business-service/users/{serviceUserId}
OR
POST /api/business-service/users/delete
Request:
{
  "serviceUserId": 2001,
  "serviceUsername": "Pr_zhangsan"
}
Response:
{
  "code": 0,
  "message": "删除成功"
}

Error Case:
{
  "code": 40001,
  "message": "删除失败!原因:业务服务正在使用中,请确保没有子业务服务用户使用业务服务!"
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| serviceUserId | number | 2001 | ✅ | 业务服务用户ID |
| serviceUsername | string | Pr_zhangsan | ✅ | 业务服务用户名 |

**测试数据**:
- 正常删除: 2001/Pr_zhangsan(无关联)
- 关联删除: 2002/Pr_lisi(有其他关联,预期失败)

---

### 5. 【公共】批量操作

**step_id**: 待创建  
**关键特性**:
- 功能: 批量暂停/恢复/删除业务服务用户
- 输入: action类型、用户ID列表
- 输出: 批量操作结果
- 类型: 批量操作类步骤

**API契约**:
```
POST /api/business-service/users/batch
Request:
{
  "action": "pause",
  "userIds": [2001, 2002, 2003]
}
OR
{
  "action": "delete",
  "userIds": [2001, 2002]
}
Response:
{
  "code": 0,
  "data": {
    "successCount": 3,
    "failedCount": 0,
    "results": [...]
  }
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| action | enum | pause | ✅ | 操作类型: pause/resume/delete |
| userIds | array | [2001, 2002, 2003] | ✅ | 用户ID列表 |

**操作类型枚举**:
- pause: 暂停
- resume: 恢复
- delete: 删除

**测试数据**:
- 批量暂停: pause/[2001,2002,2003]
- 批量恢复: resume/[2001,2002]
- 批量删除: delete/[2004,2005]

---

### 6. 【公共】业务服务用户查询

**step_id**: 待创建  
**关键特性**:
- 功能: 查询业务服务用户
- 输入: query_type(用户名/业务服务名)、query_value
- 输出: 查询结果列表
- 类型: 查询类步骤

**API契约**:
```
GET /api/business-service/users/search?queryType=username&queryValue=zhangsan
OR
POST /api/business-service/users/search
Request:
{
  "queryType": "username",
  "queryValue": "zhangsan"
}
Response:
{
  "code": 0,
  "data": {
    "total": 2,
    "list": [
      {
        "serviceUserId": 2001,
        "serviceUsername": "Pr_zhangsan",
        "serviceType": "printer",
        "status": "normal",
        "internetUsername": "zhangsan"
      },
      {
        "serviceUserId": 2002,
        "serviceUsername": "Em_zhangsan_1",
        "serviceType": "email",
        "status": "normal",
        "internetUsername": "zhangsan"
      }
    ]
  }
}
```

**变量清单**:
| 变量名 | 类型 | 默认值 | 用例级需覆盖 | 说明 |
|--------|------|---------|--------------|------|
| queryType | enum | username | ✅ | 查询类型: username/serviceType |
| queryValue | string | zhangsan | ✅ | 查询值 |

**查询类型枚举**:
- username: 按用户名查询
- serviceType: 按业务服务类型查询

**测试数据**:
- 用户名查询: username/zhangsan
- 业务服务名查询: serviceType/打印机

---

## 🚨 关键注意事项

### API支持确认
⚠️ **所有API契约都是基于推测**,需要通过以下方式确认:
1. 查阅SDET平台API文档
2. 通过工具(如Postman)测试API
3. 确认请求/响应格式
4. 验证错误码和错误消息

### 测试数据准备
⚠️ **测试数据需要提前准备**:
1. 管理员账号: admin/password
2. 测试上网用户: zhangsan/pass123
3. 模板套餐: 默认模板
4. 业务服务类型: 打印机、IP、邮箱

### 变量注入规范
⚠️ **变量注入必须使用环境变量**:
```python
# 错误示例(硬编码)
admin_username = "admin"

# 正确示例(环境变量)
admin_username = os.getenv('ADMIN_USERNAME', 'admin')
```

### 错误处理
⚠️ **必须处理所有可能的错误**:
- 400: 参数错误
- 401: 认证失败
- 404: 资源不存在
- 409: 资源冲突(如重复)
- 500: 服务器错误

---

## 📊 步骤创建检查清单

在执行 `create_phase1_public_steps.py` 前,请确认:

- [ ] API文档已查阅,所有端点和参数已确认
- [ ] 测试数据已准备(管理员账号、测试用户等)
- [ ] 环境变量已配置
- [ ] 错误处理逻辑已设计
- [ ] 变量注入规范已遵循
- [ ] 单条创建已测试通过

---

## 📂 物料存储位置

本引导文件将保存到:
```
workspace/analysis/20260318_多业务服务/materials/
└── 01_step_creation_guide.md
```

**下一步**: 执行 `create_phase1_public_steps.py` 批量创建6个公共步骤

---

**最后更新**: 2026-03-18
