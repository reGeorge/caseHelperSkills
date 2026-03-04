#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新自动化用例名称
修复用例名称缺失问题
"""

import sys
import os
import json
import time
import requests
import urllib3

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="
CREATOR_NAME = "魏斌"
CREATOR_ID = "46"

HEADERS = {
    "token": TOKEN,
    "Content-Type": "application/json"
}

def get_case_detail(case_id):
    """查询用例详情"""
    url = f"{BASE_URL}/case/{case_id}"
    
    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                return res_json.get("data")
        return None
    except Exception as e:
        print(f"  [ERROR] 查询失败: {e}")
        return None

def update_case(case_data):
    """更新用例"""
    url = f"{BASE_URL}/case"
    
    try:
        # 使用POST方法更新
        resp = requests.post(url, headers=HEADERS, json=case_data, verify=False, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                return True
            else:
                print(f"  [ERROR] 更新失败: {res_json.get('resMessage')}")
                return False
        else:
            print(f"  [ERROR] HTTP错误: {resp.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] 更新异常: {e}")
        return False

# 读取创建结果
print("读取创建结果...")
with open('sandbox/workspace/creation_result_1772604609.json', encoding='utf-8') as f:
    creation_result = json.load(f)

# 读取飞书数据
print("读取飞书数据...")
with open('sandbox/workspace/lark_latest_data.json', encoding='utf-8') as f:
    lark_data = json.load(f)

# 构建用例编号到详情的映射
case_details_map = {}
for case in lark_data:
    case_number_full = case.get('用例编号', '')
    if case_number_full and 'TP-' in case_number_full:
        tp_number = 'TP-' + case_number_full.split('TP-')[1]
        case_details_map[tp_number] = case

print(f"找到 {len(case_details_map)} 个用例详情")
print()

# 更新用例名称
print("=" * 80)
print("开始更新用例名称")
print("=" * 80)

new_cases = creation_result["cases"]
print(f"待更新用例数: {len(new_cases)}")
print()

success_count = 0
fail_count = 0

for case_info in new_cases:
    case_number = case_info["case_number"]
    case_id = case_info["case_id"]
    
    print(f"\n处理 {case_number} (ID: {case_id}):")
    
    # 查询用例详情
    print(f"  查询用例详情...")
    case_detail = get_case_detail(case_id)
    
    if not case_detail:
        print(f"  [ERROR] 无法获取用例详情")
        fail_count += 1
        continue
    
    # 获取飞书中的用例名称
    lark_case = case_details_map.get(case_number)
    if not lark_case:
        print(f"  [ERROR] 未找到飞书数据")
        fail_count += 1
        continue
    
    # 构建完整用例名称
    case_name_from_lark = lark_case.get('用例名称', '')
    # 如果是JSON格式，提取文本
    if case_name_from_lark.startswith('['):
        try:
            name_parts = json.loads(case_name_from_lark)
            case_name_text = ''.join([p.get('text', '') for p in name_parts if p.get('type') == 'text'])
        except:
            case_name_text = case_name_from_lark
    else:
        case_name_text = case_name_from_lark
    
    # 构建新名称: TP-XXX-用例名称
    new_name = f"{case_number}-{case_name_text}"
    
    print(f"  原名称: {case_detail.get('name')}")
    print(f"  新名称: {new_name[:50]}...")
    
    # 准备更新数据
    update_data = {
        "productId": case_detail.get("productId", 1),
        "id": int(case_id),
        "name": new_name,
        "priority": case_detail.get("priority", 2),
        "note": case_detail.get("note", ""),
        "isPublic": case_detail.get("isPublic", 0),
        "caseType": case_detail.get("caseType", 2),
        "status": case_detail.get("status", 0),
        "deleted": case_detail.get("deleted", 0),
        "creator": case_detail.get("creator", CREATOR_NAME),
        "createTime": case_detail.get("createTime", ""),
        "modifier": CREATOR_NAME,
        "modifyTime": case_detail.get("modifyTime", ""),
        "parent": case_detail.get("parent"),
        "order": case_detail.get("order", 1)
    }
    
    # 更新用例
    print(f"  更新用例...")
    if update_case(update_data):
        print(f"  [OK] 更新成功")
        success_count += 1
    else:
        print(f"  [ERROR] 更新失败")
        fail_count += 1
    
    time.sleep(0.3)

print("\n\n" + "=" * 80)
print("更新完成")
print("=" * 80)
print(f"\n统计:")
print(f"  成功数量: {success_count}")
print(f"  失败数量: {fail_count}")
print(f"  总计: {len(new_cases)}")
