---
name: "lark-sheets"
description: "获取飞书表格的所有工作表列表。Invoke when user needs to list sheets in a Feishu/Lark spreadsheet or requests sheet information."
---

# 飞书表格工作表列表获取器

这个skill帮助用户获取飞书表格中的所有工作表（sheet）列表。

## 功能说明

- 获取指定飞书表格的所有工作表信息
- 返回每个工作表的ID和名称
- 支持多个API端点自动尝试
- 提供详细的错误处理和调试信息

## 使用场景

当用户需要：
- 查看飞书表格中有哪些工作表
- 获取特定工作表的ID
- 了解表格结构
- 为后续操作准备工作表信息

## 使用方法

1. 确保已安装requests库：`pip install requests`
2. 配置spreadsheet_token（表格token）
3. 配置access_token（通过lark-access-token skill获取）
4. 运行脚本获取工作表列表

## 参数说明

- `spreadsheet_token`: 飞书表格的唯一标识符
- `access_token`: 飞书API访问令牌

## API端点

```
GET https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query
```

## 返回结果

成功时返回每个工作表的：
- `sheet_id`: 工作表ID
- `title`: 工作表名称
- `index`: 工作表索引
- `grid_properties`: 网格属性（行数、列数等）

## 示例输出

```
Sheet ID: 9LD59B
Sheet 名称: 新增AD源

Sheet ID: KFphLl
Sheet 名称: 编辑AD源
```

## 注意事项

- 确保access_token有效且未过期
- 确保应用已开通sheets:spreadsheet权限
- 确保表格存在且用户有访问权限
- spreadsheet_token可以从飞书表格URL中获取
