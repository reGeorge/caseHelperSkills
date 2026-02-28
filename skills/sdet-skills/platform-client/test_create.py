#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试创建操作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platform_client import PlatformClient

# 配置
PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"
PLATFORM_TOKEN = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
PARENT_DIR_ID = 66241

# 创建客户端
client = PlatformClient(
    base_url=PLATFORM_URL,
    token=PLATFORM_TOKEN,
    creator_name="魏斌",
    creator_id="46"
)

print("=" * 80)
print("测试创建目录")
print("=" * 80)

result = client.create_directory(
    name="测试目录-Script创建",
    parent_id=PARENT_DIR_ID,
    note="通过脚本创建的测试目录"
)

print(f"成功: {result['success']}")
print(f"消息: {result['message']}")
if result['success']:
    print(f"新目录ID: {result['data']}")

print("\n" + "=" * 80)
print("测试创建用例")
print("=" * 80)

result = client.create_case(
    name="测试用例-Script创建",
    directory_id=PARENT_DIR_ID,
    description="自动化测试用例",
    note="通过脚本创建"
)

print(f"成功: {result['success']}")
print(f"消息: {result['message']}")
if result['success']:
    print(f"新用例ID: {result['data']}")
