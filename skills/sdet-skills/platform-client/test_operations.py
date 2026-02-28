#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试自动化平台操作 - 使用实际用例ID
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platform_client import PlatformClient

# 配置
PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"  # 实际平台地址
PLATFORM_TOKEN = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
PARENT_DIR_ID = 66241  # 父目录ID
CASE_ID = 66242  # 测试用例ID

# 创建客户端
client = PlatformClient(
    base_url=PLATFORM_URL,
    token=PLATFORM_TOKEN,
    creator_name="魏斌",
    creator_id="46"
)


def test_get_directory():
    """测试获取目录"""
    print("=" * 80)
    print("测试1: 获取目录 (ID: {})".format(PARENT_DIR_ID))
    print("=" * 80)

    result = client.get_directory(PARENT_DIR_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success'] and result['data']:
        print(f"目录名称: {result['data'].get('name')}")
        print(f"目录ID: {result['data'].get('id')}")


def test_list_directories():
    """测试列出目录"""
    print("\n" + "=" * 80)
    print("测试2: 列出目录 (父ID: {})".format(PARENT_DIR_ID))
    print("=" * 80)

    result = client.list_directories(parent_id=PARENT_DIR_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"目录数量: {len(result['data'])}")
        for dir_info in result['data'][:5]:  # 只显示前5个
            print(f"  - ID: {dir_info.get('id')}, 名称: {dir_info.get('name')}")


def test_get_case():
    """测试获取用例"""
    print("\n" + "=" * 80)
    print("测试3: 获取用例 (ID: {})".format(CASE_ID))
    print("=" * 80)

    result = client.get_case(CASE_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success'] and result['data']:
        print(f"用例名称: {result['data'].get('name')}")
        print(f"用例ID: {result['data'].get('id')}")
        print(f"用例描述: {result['data'].get('description', 'N/A')}")


def test_list_cases():
    """测试列出用例"""
    print("\n" + "=" * 80)
    print("测试4: 列出用例 (目录ID: {})".format(PARENT_DIR_ID))
    print("=" * 80)

    result = client.list_cases(directory_id=PARENT_DIR_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"用例数量: {len(result['data'])}")
        for case_info in result['data'][:5]:  # 只显示前5个
            print(f"  - ID: {case_info.get('id')}, 名称: {case_info.get('name')}")


def test_list_steps():
    """测试列出步骤"""
    print("\n" + "=" * 80)
    print("测试5: 列出步骤 (用例ID: {})".format(CASE_ID))
    print("=" * 80)

    result = client.list_steps(CASE_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"步骤数量: {len(result['data'])}")
        for step_info in result['data'][:5]:  # 只显示前5个
            print(f"  - ID: {step_info.get('id')}, 名称: {step_info.get('name')}, 方法: {step_info.get('method')}")


def test_list_variables():
    """测试列出变量"""
    print("\n" + "=" * 80)
    print("测试6: 列出变量 (用例ID: {})".format(CASE_ID))
    print("=" * 80)

    result = client.list_variables(CASE_ID)
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"变量数量: {len(result['data'])}")
        for var_info in result['data'][:5]:  # 只显示前5个
            print(f"  - ID: {var_info.get('id')}, 名称: {var_info.get('name')}, 值: {var_info.get('value')}")


def test_create_directory():
    """测试创建目录"""
    print("\n" + "=" * 80)
    print("测试7: 创建目录")
    print("=" * 80)

    result = client.create_directory(
        name="测试目录-自动创建",
        parent_id=PARENT_DIR_ID,
        note="由自动化脚本创建"
    )
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"新目录ID: {result['data']}")
        return result['data']
    return None


def test_create_case():
    """测试创建用例"""
    print("\n" + "=" * 80)
    print("测试8: 创建用例")
    print("=" * 80)

    result = client.create_case(
        name="测试用例-自动创建",
        directory_id=PARENT_DIR_ID,
        description="自动化测试用例",
        note="由脚本创建",
        priority=2
    )
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    if result['success']:
        print(f"新用例ID: {result['data']}")
        return result['data']
    return None


def main():
    """运行所有测试"""
    print("=" * 80)
    print("自动化平台操作测试")
    print(f"平台地址: {PLATFORM_URL}")
    print(f"父目录ID: {PARENT_DIR_ID}")
    print(f"测试用例ID: {CASE_ID}")
    print("=" * 80)

    # 查询操作测试（不修改数据）
    test_get_directory()
    test_list_directories()
    test_get_case()
    test_list_cases()
    test_list_steps()
    test_list_variables()

    # 询问是否执行创建测试（会修改数据）
    print("\n" + "=" * 80)
    print("注意: 以下操作会创建新数据，请确认")
    print("取消: 在脚本中注释掉相应的函数调用")
    print("=" * 80)

    # 取消注释以下函数来测试创建操作
    # test_create_directory()
    # test_create_case()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
