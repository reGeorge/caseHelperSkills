#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量创建自动化目录和用例
在父目录66469下创建按配置状态分类的目录结构和用例
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

PARENT_DIRECTORY_ID = "66469"

def create_directory(name, parent_id):
    """创建目录"""
    url = f"{BASE_URL}/case"
    
    payload = {
        "name": name,
        "caseType": 0,  # 0=目录
        "parent": parent_id,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID,
        "status": 0,
        "deleted": 0
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, verify=False, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                return res_json.get("data")
            else:
                print(f"    [ERROR] 创建目录失败: {res_json.get('resMessage')}")
                return None
        else:
            print(f"    [ERROR] HTTP错误: {resp.status_code}")
            return None
    except Exception as e:
        print(f"    [ERROR] 异常: {e}")
        return None

def create_case(case_data, directory_id):
    """创建用例"""
    url = f"{BASE_URL}/case"
    
    payload = {
        "productId": 1,
        "componentId": "1",
        "name": case_data["name"],
        "priority": case_data.get("priority", 2),
        "note": case_data.get("description", ""),
        "caseType": 1,  # 1=自动化用例
        "type": 1,  # 1=自动化用例
        "parent": directory_id,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID,
        "status": 0,
        "deleted": 0
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, verify=False, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                return res_json.get("data")
            else:
                return None
        else:
            return None
    except Exception as e:
        return None

# 读取数据
print("读取数据文件...")
with open('sandbox/workspace/test_case_analysis.json', encoding='utf-8') as f:
    analysis_data = json.load(f)

with open('sandbox/workspace/case_id_mapping.json', encoding='utf-8') as f:
    mapping_raw = json.load(f)
    mapping_data = mapping_raw.get('mapping', [])

with open('sandbox/workspace/lark_latest_data.json', encoding='utf-8') as f:
    lark_data = json.load(f)

# 构建映射 - 使用manual_case_code
manual_to_auto = {}
for item in mapping_data:
    code = item.get('manual_case_code', '')
    # 提取TP编号
    if 'TP-' in code:
        tp_number = 'TP-' + code.split('TP-')[1]
        manual_to_auto[tp_number] = item.get('auto_case_id')

case_details = {case['用例编号']: case for case in lark_data if case.get('用例编号')}

print(f"数据加载完成: {len(case_details)}个用例")
print()

# 创建结果
creation_result = {
    "directories": {},
    "cases": [],
    "skipped": [],
    "errors": []
}

# 定义目录结构
directory_structure = {
    "无感接入类型=仅有线": ["TP-001", "TP-002", "TP-014", "TP-015", "TP-024"],
    "无感接入类型=仅无线": ["TP-003", "TP-004", "TP-005", "TP-013", "TP-016", "TP-018", "TP-019", "TP-025", "TP-026", "TP-027"],
    "无感接入类型=全部": ["TP-006", "TP-017", "TP-028"],
    "MAC快速认证数=满足": {
        "无感接入类型=仅有线": ["TP-007", "TP-009", "TP-011"],
        "无感接入类型=仅无线": ["TP-008", "TP-010"],
        "无感接入类型=全部": ["TP-012"]
    },
    "MAC快速接入=未勾选": {
        "无感接入类型=仅有线": ["TP-021"],
        "无感接入类型=仅无线": ["TP-022"],
        "无感接入类型=全部": ["TP-023"]
    },
    "默认配置": ["TP-020"]
}

print("=" * 80)
print("开始创建目录和用例")
print("=" * 80)

# 创建一级目录
print("\n[步骤1] 创建一级目录")
print("-" * 80)
for dir_name, cases in directory_structure.items():
    print(f"\n创建目录: {dir_name}")
    dir_id = create_directory(dir_name, PARENT_DIRECTORY_ID)
    
    if dir_id:
        creation_result["directories"][dir_name] = {
            "id": dir_id,
            "name": dir_name
        }
        print(f"  [OK] ID: {dir_id}")
    else:
        creation_result["errors"].append(f"目录创建失败: {dir_name}")
    
    time.sleep(0.3)

# 创建子目录
print("\n\n[步骤2] 创建子目录")
print("-" * 80)
for dir_name, sub_dirs in directory_structure.items():
    if isinstance(sub_dirs, dict):  # 有子目录
        parent_id = creation_result["directories"][dir_name]["id"]
        
        for sub_name in sub_dirs.keys():
            full_name = f"{dir_name}/{sub_name}"
            print(f"\n创建子目录: {sub_name} (父ID: {parent_id})")
            sub_id = create_directory(sub_name, parent_id)
            
            if sub_id:
                creation_result["directories"][full_name] = {
                    "id": sub_id,
                    "name": sub_name,
                    "parent_id": parent_id
                }
                print(f"  [OK] ID: {sub_id}")
            else:
                creation_result["errors"].append(f"子目录创建失败: {full_name}")
            
            time.sleep(0.3)

# 创建用例
print("\n\n[步骤3] 创建用例")
print("-" * 80)

for dir_name, cases in directory_structure.items():
    if isinstance(cases, list):  # 直接用例
        dir_id = creation_result["directories"][dir_name]["id"]
        
        print(f"\n在目录 {dir_name} 下创建用例:")
        for case_number in cases:
            # 检查是否已有自动化
            if case_number in manual_to_auto:
                print(f"  [SKIP] {case_number} 已有自动化ID: {manual_to_auto[case_number]}")
                creation_result["skipped"].append({
                    "case_number": case_number,
                    "auto_id": manual_to_auto[case_number]
                })
                continue
            
            # 创建用例
            case_detail = case_details.get(case_number, {})
            case_name = f"{case_number}-{case_detail.get('用例名称', '')}"
            
            print(f"  创建: {case_name[:50]}...")
            case_id = create_case({
                "name": case_name,
                "description": f"手工用例编号: {case_number}\n\n{case_detail.get('用例描述', '')}",
                "priority": 2
            }, dir_id)
            
            if case_id:
                print(f"    [OK] ID: {case_id}")
                creation_result["cases"].append({
                    "case_number": case_number,
                    "case_id": case_id,
                    "directory_id": dir_id,
                    "case_name": case_name
                })
            else:
                print(f"    [ERROR] 创建失败")
                creation_result["errors"].append(f"用例创建失败: {case_number}")
            
            time.sleep(0.3)
    
    elif isinstance(cases, dict):  # 子目录用例
        for sub_name, case_numbers in cases.items():
            full_name = f"{dir_name}/{sub_name}"
            dir_id = creation_result["directories"][full_name]["id"]
            
            print(f"\n在目录 {sub_name} 下创建用例:")
            for case_number in case_numbers:
                # 检查是否已有自动化
                if case_number in manual_to_auto:
                    print(f"  [SKIP] {case_number} 已有自动化ID: {manual_to_auto[case_number]}")
                    creation_result["skipped"].append({
                        "case_number": case_number,
                        "auto_id": manual_to_auto[case_number]
                    })
                    continue
                
                # 创建用例
                case_detail = case_details.get(case_number, {})
                case_name = f"{case_number}-{case_detail.get('用例名称', '')}"
                
                print(f"  创建: {case_name[:50]}...")
                case_id = create_case({
                    "name": case_name,
                    "description": f"手工用例编号: {case_number}\n\n{case_detail.get('用例描述', '')}",
                    "priority": 2
                }, dir_id)
                
                if case_id:
                    print(f"    [OK] ID: {case_id}")
                    creation_result["cases"].append({
                        "case_number": case_number,
                        "case_id": case_id,
                        "directory_id": dir_id,
                        "case_name": case_name
                    })
                else:
                    print(f"    [ERROR] 创建失败")
                    creation_result["errors"].append(f"用例创建失败: {case_number}")
                
                time.sleep(0.3)

# 统计
print("\n\n" + "=" * 80)
print("创建完成")
print("=" * 80)
print(f"\n统计:")
print(f"  目录创建: {len(creation_result['directories'])}个")
print(f"  用例创建: {len(creation_result['cases'])}个")
print(f"  已跳过: {len(creation_result['skipped'])}个")
print(f"  失败数量: {len(creation_result['errors'])}个")

if creation_result["errors"]:
    print(f"\n错误列表:")
    for error in creation_result["errors"][:10]:  # 只显示前10个
        print(f"  - {error}")

# 保存结果
output_file = f'sandbox/workspace/creation_result_{int(time.time())}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(creation_result, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存到: {output_file}")
