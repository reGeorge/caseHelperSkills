# 自动化用例标题生成器

## 功能说明

自动生成测试用例的脚本名称和脚本步骤,支持写入飞书表格。

## 核心功能

### 1. 脚本名称生成规则

**格式**: `{用例名称} - {期望结果最后一句话}`

**示例**:
- 用例名称: `新增接入类型仅无线，修改为仅有线，无感接入类型为仅有线，用户进行无线portal认证`
- 期望结果最后一句话: `用户进行无线portal认证成功，注册失败`
- 生成的脚本名称: `新增接入类型仅无线，修改为仅有线，无感接入类型为仅有线，用户进行无线portal认证 - 用户进行无线portal认证成功，注册失败`

### 2. 脚本步骤生成规则

将脚本名称按分隔符(句号、逗号、顿号等)拆分成多个步骤,格式:
```
1. 步骤一
2. 步骤二
3. 步骤三
...
```

**示例**:
```
1. 新增接入类型仅无线
2. 修改为仅有线
3. 无感接入类型为仅有线
4. 用户进行无线portal认证 - 用户进行无线portal认证成功
5. 注册失败
```

## API接口

### ScriptNameGenerator类

#### 初始化

```python
from script_name_generator import ScriptNameGenerator

generator = ScriptNameGenerator(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

#### 主要方法

##### generate_from_sheet(spreadsheet_token, sheet_id)

从飞书表格读取数据,生成脚本名称和步骤,并写回表格。

```python
result = generator.generate_from_sheet(
    spreadsheet_token="Mw7escaVhh92SSts8incmbbUnkc",
    sheet_id="dfa872"
)

print(f"处理了 {result['total_count']} 条用例")
print(f"成功 {result['success_count']} 条")
```

##### generate_from_local(json_file)

从本地JSON文件读取数据,生成脚本名称和步骤。

```python
result = generator.generate_from_local("test_cases.json")

# 结果保存到: test_cases_with_script_info.json
```

##### extract_last_expect_result(expect_result)

提取期望结果的最后一句话。

```python
last_result = generator.extract_last_expect_result(
    "1.步骤一成功\n2.步骤二成功\n3.最终结果成功"
)
# 返回: "最终结果成功"
```

##### generate_script_name(case_name, expect_result)

生成脚本名称。

```python
script_name = generator.generate_script_name(
    "用例名称",
    "1.结果一\n2.结果二"
)
# 返回: "用例名称 - 结果二"
```

##### split_into_steps(text)

将文本拆分成步骤。

```python
steps = generator.split_into_steps("步骤一，步骤二，步骤三")
# 返回:
# 1. 步骤一
# 2. 步骤二
# 3. 步骤三
```

## 使用示例

### 示例1: 处理飞书表格

```python
import os
from script_name_generator import ScriptNameGenerator

# 初始化
generator = ScriptNameGenerator(
    app_id=os.getenv('LARK_APP_ID'),
    app_secret=os.getenv('LARK_APP_SECRET')
)

# 处理飞书表格
result = generator.generate_from_sheet(
    spreadsheet_token="Mw7escaVhh92SSts8incmbbUnkc",
    sheet_id="dfa872"
)

print(f"处理结果: {result}")
```

### 示例2: 处理本地JSON文件

```python
from script_name_generator import ScriptNameGenerator

# 初始化(不需要凭证)
generator = ScriptNameGenerator()

# 处理本地文件
result = generator.generate_from_local("test_cases.json")

# 查看结果
for case in result['cases'][:3]:
    print(f"用例: {case['用例编号']}")
    print(f"脚本名称: {case['脚本名称']}")
    print(f"脚本步骤:\n{case['脚本步骤']}\n")
```

### 示例3: 单独使用辅助函数

```python
from script_name_generator import ScriptNameGenerator

generator = ScriptNameGenerator()

# 提取最后一句话
text = "1.配置成功\n2.认证成功\n3.注册成功"
last = generator.extract_last_expect_result(text)
print(f"最后一句话: {last}")

# 生成脚本名称
script_name = generator.generate_script_name(
    "测试无感认证",
    "1.步骤一\n2.步骤二成功"
)
print(f"脚本名称: {script_name}")

# 拆分步骤
steps = generator.split_into_steps("配置参数，执行测试，验证结果")
print(f"脚本步骤:\n{steps}")
```

## 数据格式

### 输入数据格式

```json
[
  {
    "用例编号": "RG-UNC-无感认证设置-TP-001",
    "用例名称": "新增接入类型仅无线，修改为仅有线，无感接入类型为仅有线，用户进行无线portal认证",
    "期望结果": "1.接入控制名jing2输入成功...\n9.用户进行无线portal认证成功，注册失败"
  }
]
```

### 输出数据格式

```json
[
  {
    "用例编号": "RG-UNC-无感认证设置-TP-001",
    "用例名称": "新增接入类型仅无线，修改为仅有线，无感接入类型为仅有线，用户进行无线portal认证",
    "期望结果": "1.接入控制名jing2输入成功...\n9.用户进行无线portal认证成功，注册失败",
    "脚本名称": "新增接入类型仅无线，修改为仅有线，无感接入类型为仅有线，用户进行无线portal认证 - 用户进行无线portal认证成功，注册失败",
    "脚本步骤": "1. 新增接入类型仅无线\n2. 修改为仅有线\n3. 无感接入类型为仅有线\n4. 用户进行无线portal认证 - 用户进行无线portal认证成功\n5. 注册失败"
  }
]
```

## 注意事项

1. **期望结果格式**: 期望结果需要包含步骤编号(如"1."、"2."等),否则会返回最后一行
2. **分隔符优先级**: 句号 > 逗号 > 顿号 > 分号
3. **括号标注**: 会自动移除括号标注(如"（正向）")
4. **飞书表格列**: 默认写入Z列(脚本名称)和AA列(脚本步骤)
5. **表头更新**: 会自动更新表头

## 依赖

- requests: HTTP请求
- json: JSON处理
- re: 正则表达式
- yaml: 配置文件读取(可选)

## 错误处理

所有方法都会捕获异常并返回错误信息:

```python
result = generator.generate_from_sheet("token", "id")
if 'error' in result:
    print(f"处理失败: {result['error']}")
else:
    print(f"处理成功: {result['total_count']} 条")
```

## 版本历史

- v1.0.0 (2026-03-03): 初始版本
  - 支持从飞书表格读取和写入
  - 支持从本地JSON文件读取
  - 自动生成脚本名称和脚本步骤
