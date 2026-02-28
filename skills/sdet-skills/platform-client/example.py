#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化平台客户端使用示例
"""

from platform_client import PlatformClient

# 配置信息
PLATFORM_URL = "https://your-platform.com"  # 替换为实际平台地址
PLATFORM_TOKEN = "NDY7d2VpYmluOjE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="
DEFAULT_PARENT_ID = 66241  # 默认父目录ID

# 创建客户端
client = PlatformClient(
    base_url=PLATFORM_URL,
    token=PLATFORM_TOKEN,
    creator_name="TestUser",
    creator_id="12345"
)


def example_directory_operations():
    """目录操作示例"""
    print("=" * 80)
    print("目录操作示例")
    print("=" * 80)

    # 1. 创建目录
    print("\n1. 创建目录:")
    result = client.create_directory(
        name="测试目录001",
        parent_id=DEFAULT_PARENT_ID,
        note="这是一个测试目录"
    )
    print(f"   结果: {result}")
    if result["success"]:
        dir_id = result["data"]
        print(f"   目录ID: {dir_id}")

        # 2. 查询目录
        print("\n2. 查询目录:")
        result = client.get_directory(dir_id)
        print(f"   结果: {result}")

        # 3. 更新目录
        print("\n3. 更新目录:")
        result = client.update_directory(
            dir_id=dir_id,
            name="测试目录001-更新",
            note="更新后的描述"
        )
        print(f"   结果: {result}")

        # 4. 列出目录
        print("\n4. 列出目录:")
        result = client.list_directories(parent_id=DEFAULT_PARENT_ID)
        print(f"   数量: {len(result['data']) if result['success'] else 0}")
        print(f"   结果: {result}")

        # 5. 删除目录（可选，注释掉以保留目录）
        # print("\n5. 删除目录:")
        # result = client.delete_directory(dir_id)
        # print(f"   结果: {result}")


def example_case_operations():
    """用例操作示例"""
    print("\n" + "=" * 80)
    print("用例操作示例")
    print("=" * 80)

    # 1. 创建用例
    print("\n1. 创建用例:")
    result = client.create_case(
        name="测试用例001",
        directory_id=DEFAULT_PARENT_ID,
        description="这是一个测试用例的描述",
        note="备注信息",
        priority=2,
        variables=[
            {"name": "host", "value": "https://api.example.com"},
            {"name": "timeout", "value": "5000"}
        ],
        request={
            "method": "POST",
            "url": "/api/test",
            "headers": {"Content-Type": "application/json"},
            "body": {"username": "test", "password": "123456"}
        },
        check=[
            {"expect": 200, "field": "status_code"}
        ]
    )
    print(f"   结果: {result}")
    if result["success"]:
        case_id = result["data"]
        print(f"   用例ID: {case_id}")

        # 2. 查询用例
        print("\n2. 查询用例:")
        result = client.get_case(case_id)
        print(f"   结果: {result}")

        # 3. 更新用例
        print("\n3. 更新用例:")
        result = client.update_case(
            case_id=case_id,
            name="测试用例001-更新",
            description="更新后的描述"
        )
        print(f"   结果: {result}")

        # 4. 列出用例
        print("\n4. 列出用例:")
        result = client.list_cases(directory_id=DEFAULT_PARENT_ID)
        print(f"   数量: {len(result['data']) if result['success'] else 0}")

        # 5. 删除用例（可选，注释掉以保留用例）
        # print("\n5. 删除用例:")
        # result = client.delete_case(case_id)
        # print(f"   结果: {result}")


def example_step_operations(case_id):
    """步骤操作示例"""
    print("\n" + "=" * 80)
    print("步骤操作示例")
    print("=" * 80)

    # 1. 创建步骤
    print("\n1. 创建步骤:")
    result = client.create_step(
        case_id=case_id,
        name="步骤1-登录",
        order=1,
        host="${G_host}",
        protocol=0,
        path="/api/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body={"username": "test", "password": "123456"},
        check=[{"expect": 200}]
    )
    print(f"   结果: {result}")
    if result["success"]:
        step_id = result["data"]
        print(f"   步骤ID: {step_id}")

        # 2. 查询步骤
        print("\n2. 查询步骤:")
        result = client.get_step(step_id)
        print(f"   结果: {result}")

        # 3. 更新步骤
        print("\n3. 更新步骤:")
        result = client.update_step(
            step_id=step_id,
            name="步骤1-登录-更新"
        )
        print(f"   结果: {result}")

        # 4. 列出步骤
        print("\n4. 列出步骤:")
        result = client.list_steps(case_id)
        print(f"   数量: {len(result['data']) if result['success'] else 0}")

        # 5. 删除步骤（可选）
        # print("\n5. 删除步骤:")
        # result = client.delete_step(step_id)
        # print(f"   结果: {result}")


def example_variable_operations(case_id):
    """变量操作示例"""
    print("\n" + "=" * 80)
    print("变量操作示例")
    print("=" * 80)

    # 1. 创建变量
    print("\n1. 创建变量:")
    result = client.create_variable(
        case_id=case_id,
        name="test_var",
        value="test_value"
    )
    print(f"   结果: {result}")
    if result["success"]:
        var_id = result["data"]
        print(f"   变量ID: {var_id}")

        # 2. 更新变量
        print("\n2. 更新变量:")
        result = client.update_variable(
            var_id=var_id,
            value="new_test_value"
        )
        print(f"   结果: {result}")

        # 3. 列出变量
        print("\n3. 列出变量:")
        result = client.list_variables(case_id)
        print(f"   数量: {len(result['data']) if result['success'] else 0}")
        if result["success"]:
            for var in result["data"]:
                print(f"   - {var.get('name')}: {var.get('value')}")

        # 4. 删除变量（可选）
        # print("\n4. 删除变量:")
        # result = client.delete_variable(var_id)
        # print(f"   结果: {result}")


def main():
    """主函数"""
    print("自动化平台客户端使用示例")
    print("=" * 80)

    # 运行目录操作示例
    example_directory_operations()

    # 运行用例操作示例
    example_case_operations()

    # 如果有具体的用例ID，可以运行步骤和变量操作示例
    # case_id = 66242  # 替换为实际的用例ID
    # example_step_operations(case_id)
    # example_variable_operations(case_id)

    print("\n" + "=" * 80)
    print("示例运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
