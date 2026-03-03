#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
删除不需要的自动化用例
"""
import json
import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="

# 通用headers
HEADERS = {
    "token": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*"
}

def delete_case(case_id):
    """
    删除用例（通过设置deleted=1）
    """
    url = f"{BASE_URL}/case/{case_id}"

    try:
        # 先查询用例是否存在
        resp = requests.get(url, headers=HEADERS, verify=False)
        if resp.status_code != 200:
            print(f"  [ERROR] 用例不存在或查询失败: {case_id}")
            return False

        # 删除用例（更新deleted字段）
        delete_url = f"{BASE_URL}/case"
        payload = {
            "id": case_id,
            "deleted": 1
        }

        resp = requests.put(delete_url, headers=HEADERS, json=payload, verify=False)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                print(f"  [OK] 用例删除成功: {case_id}")
                return True
            else:
                print(f"  [FAIL] 用例删除失败: {case_id} - {res_json.get('resMessage')}")
        else:
            print(f"  [ERROR] 用例删除HTTP错误: {case_id} - 状态码={resp.status_code}")
    except Exception as e:
        print(f"  [EXCEPTION] 用例删除异常: {case_id} - {e}")

    return False


def main():
    """主函数"""
    # 加载删除列表
    with open('sandbox/workspace/case_creation_plan.json', 'r', encoding='utf-8') as f:
        plan = json.load(f)

    to_delete = plan['to_delete']

    print('='*80)
    print('删除不需要的自动化用例')
    print('='*80)
    print(f'待删除用例数: {len(to_delete)}')
    print()

    deleted_count = 0
    for i, case in enumerate(to_delete, 1):
        print(f'[{i}/{len(to_delete)}] [{case["manual_case_code"]}] {case["manual_case_name"]}')
        if delete_case(case['auto_case_id']):
            deleted_count += 1

    print()
    print('='*80)
    print('删除完成汇总')
    print('='*80)
    print(f'成功删除: {deleted_count}/{len(to_delete)}')
    print(f'删除失败: {len(to_delete) - deleted_count}')

    print(f'\n保留的用例数: {len(plan["to_keep"])}')


if __name__ == "__main__":
    main()
