#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证创建的资源
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platform_client import PlatformClient

# 配置
PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"
PLATFORM_TOKEN = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="

# 创建客户端
client = PlatformClient(
    base_url=PLATFORM_URL,
    token=PLATFORM_TOKEN,
    creator_name="魏斌",
    creator_id="46"
)

print("=" * 80)
print("验证创建的目录 (ID: 66243)")
print("=" * 80)

result = client.get_directory(66243)
print(f"成功: {result['success']}")
if result['success']:
    data = result['data']
    print(f"名称: {data.get('name')}")
    print(f"父ID: {data.get('parent')}")
    print(f"描述: {data.get('note')}")

print("\n" + "=" * 80)
print("验证创建的用例 (ID: 66244)")
print("=" * 80)

result = client.get_case(66244)
print(f"成功: {result['success']}")
if result['success']:
    data = result['data']
    print(f"名称: {data.get('name')}")
    print(f"父ID: {data.get('parent')}")
    print(f"描述: {data.get('description')}")
    print(f"备注: {data.get('note')}")

print("\n" + "=" * 80)
print("列出用例步骤 (用例ID: 66244)")
print("=" * 80)

result = client.list_steps(66244)
print(f"成功: {result['success']}")
if result['success']:
    print(f"步骤数量: {len(result['data'])}")

print("\n" + "=" * 80)
print("列出用例变量 (用例ID: 66244)")
print("=" * 80)

result = client.list_variables(66244)
print(f"成功: {result['success']}")
if result['success']:
    print(f"变量数量: {len(result['data'])}")
    for var in result['data']:
        print(f"  - {var.get('name')}: {var.get('value')}")
