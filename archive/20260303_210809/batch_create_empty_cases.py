#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量创建空白自动化用例
从手工用例生成对应的自动化用例框架
"""

import json
import requests
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="
CREATOR_NAME = "魏斌"
CREATOR_ID = 46

# 目标目录ID
TARGET_DIRECTORY_ID = 66388

# 通用headers
HEADERS = {
    "token": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*"
}


def load_manual_cases():
    """加载手工用例数据"""
    with open('sandbox/workspace/test_cases_with_script_info.json', encoding='utf-8') as f:
        data = json.load(f)
    
    # 过滤出手工用例
    manual_cases = [c for c in data if c.get('手工/自动化') == '手工']
    return manual_cases


def create_case(case_data, parent_id):
    """
    创建自动化用例
    
    Args:
        case_data: 手工用例数据
        parent_id: 父目录ID
    
    Returns:
        用例ID
    """
    url = f"{BASE_URL}/case"
    
    # 构造用例名称（使用手工用例的名称）
    case_name = case_data.get('用例名称', '未命名用例')
    
    # 用例描述
    description = case_data.get('用例描述', '')
    
    # 用例编号
    case_code = case_data.get('用例编号', '')
    
    # 用例等级
    priority_map = {'p0': 0, 'p1': 1, 'p2': 2, 'p3': 3}
    case_level = case_data.get('用例等级', 'p2').lower()
    priority = priority_map.get(case_level, 2)
    
    # 备注信息
    note = f"手工用例编号: {case_code}\n用例描述: {description}"
    
    payload = {
        "productId": 1,
        "name": case_name,
        "priority": priority,
        "note": note,
        "caseType": 1,  # 1表示自动化用例
        "parent": parent_id,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID,
        "status": 0,
        "deleted": 0
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                case_id = res_json.get("data")
                print(f"  [OK] 用例创建成功: {case_name} (ID: {case_id})")
                return case_id
            else:
                print(f"  [FAIL] 用例创建失败: {case_name} - {res_json.get('resMessage')}")
        else:
            print(f"  [ERROR] 用例创建HTTP错误: {case_name} - 状态码={resp.status_code}")
    except Exception as e:
        print(f"  [EXCEPTION] 用例创建异常: {case_name} - {e}")
    
    return None


def main():
    """主函数：批量创建空白自动化用例"""
    print(f"\n{'#'*60}")
    print(f"# 批量创建空白自动化用例")
    print(f"# 目标目录ID: {TARGET_DIRECTORY_ID}")
    print(f"{'#'*60}\n")
    
    # 1. 加载手工用例
    print("步骤1: 加载手工用例数据...")
    manual_cases = load_manual_cases()
    print(f"  找到 {len(manual_cases)} 个手工用例\n")
    
    # 2. 批量创建用例
    print(f"步骤2: 批量创建自动化用例...")
    print(f"{'='*60}")
    
    created_cases = []
    failed_cases = []
    
    for idx, case in enumerate(manual_cases, 1):
        print(f"\n[{idx}/{len(manual_cases)}] ", end='')
        
        case_id = create_case(case, TARGET_DIRECTORY_ID)
        
        if case_id:
            created_cases.append({
                'manual_case_code': case.get('用例编号'),
                'manual_case_name': case.get('用例名称'),
                'auto_case_id': case_id
            })
        else:
            failed_cases.append(case.get('用例名称'))
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 3. 汇总结果
    print(f"\n{'='*60}")
    print(f"创建完成汇总")
    print(f"{'='*60}")
    print(f"成功创建: {len(created_cases)}/{len(manual_cases)}")
    print(f"失败数量: {len(failed_cases)}")
    
    if failed_cases:
        print(f"\n失败用例:")
        for name in failed_cases:
            print(f"  - {name}")
    
    # 4. 保存创建结果
    if created_cases:
        result_file = f'sandbox/workspace/batch_create_result_{int(time.time())}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(created_cases, f, ensure_ascii=False, indent=2)
        print(f"\n创建结果已保存到: {result_file}")
    
    # 5. 访问链接
    print(f"\n建议下一步操作:")
    print(f"1. 访问目标目录: https://sdet.ruishan.cc/ap/atp/apiCase?parent={TARGET_DIRECTORY_ID}")
    print(f"2. 为每个用例添加步骤和变量")
    print(f"3. 触发调试验证")


if __name__ == "__main__":
    main()
