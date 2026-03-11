# 平台客户端 Skill

用于 SDET 平台的目录、用例、步骤、变量管理。

## 质量门槛（G1）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| base_url | string | 是 | 无 | 平台地址，例如 https://host/api/sdet-atp |
| token | string | 是 | 无 | 平台 token |
| creator_name | string | 否 | System | 创建/修改人名称 |
| creator_id | string | 否 | 0 | 创建/修改人 ID |

构造方式：

```python
from platform_client import PlatformClient

client = PlatformClient(
    base_url=Config.TEST_PLATFORM_URL,
    token=Config.TEST_PLATFORM_TOKEN,
    creator_name=Config.CREATOR_NAME,
    creator_id=str(Config.CREATOR_ID),
)
```

## 目录接口

- create_directory(name: str, parent_id: int, note: str = "", priority: int = 2)
- update_directory(dir_id: int, name: str | None = None, note: str | None = None, priority: int | None = None)
- delete_directory(dir_id: int)
- get_directory(dir_id: int)
- list_directories(parent_id: int | None = None)

## 用例接口

- create_case(name: str, directory_id: int, description: str = "", note: str = "", priority: int = 2, variables: list | None = None, request: dict | None = None, check: list | None = None)
- update_case(case_id: int, name: str | None = None, description: str | None = None, note: str | None = None, priority: int | None = None)
- delete_case(case_id: int)
- get_case(case_id: int)
- list_cases(directory_id: int | None = None)

## 步骤接口

- create_step(case_id: int, name: str, order: int, host: str = "${G_host}", protocol: int = 0, path: str = "", method: int = 1, headers: dict | None = None, body: dict | None = None, params: dict | None = None, variables: list | None = None, check: list | None = None, type: int = 0, quote_id: int | None = None)
- update_step(step_id: int, **kwargs)
- delete_step(step_id: int)
- get_step(step_id: int)
- list_steps(case_id: int)

method 为整数：0=GET, 1=POST, 2=PUT, 3=DELETE。

## 变量接口（实现对齐）

- create_variable(case_id: int, name: str, value: str)
- update_variable(var_id: int, value: str | None = None, case_id: int | None = None, name: str | None = None, note: str | None = None)
- delete_variable(var_id: int)
- list_variables(case_id: int)
- get_case_variables_v2(case_id: int)

平台契约说明：

- 变量查询：GET /case/variables/{case_id}
- 变量更新：POST /case/variable（body 必须带 id）

## 更新语义说明（实现对齐）

平台不支持标准 PUT 更新实体时，统一采用：

1. GET 查询完整对象
2. 在客户端修改字段
3. POST 提交到集合端点

## G2 最小契约验证

执行：

```bash
python scripts/verify/contract_smoke.py
```

产物：

- sandbox/workspace/contract_report.json

## G3 规则化审计入口

执行：

```bash
python scripts/verify/run_case_debugger_audit.py
```

规则文件：

- knowledge/audit/config_rules.json
