#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量创建用例到SDET平台66328目录
"""

import sys
import os
import json
import yaml
from platform_client import PlatformClient

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取配置
config_path = os.path.join(script_dir, '../../agent_service/config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

base_url = config['secrets']['SDET_BASE_URL']
token = config['secrets']['SDET_API_TOKEN']

# 初始化PlatformClient
client = PlatformClient(
    base_url=base_url,
    token=token,
    creator_name='自动化脚本',
    creator_id='9999')

# 读取输入文件
with open('wired_auth_cases.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# 目标目录ID
target_directory_id = 66328

# 存储结果
results = []
success_count = 0
failed_count = 0

# 遍历每条用例并创建
for idx, case in enumerate(cases):
    row_number = idx + 1  # 从1开始计数
    case_name = case.get('用例名称', '')
    case_description = case.get('用例描述', '')
    case_note = f"用例编号: {case.get('用例编号', '')}\n测试等级: {case.get('用例等级', '')}\n备注: {case.get('备注', '')}"
    
    # 解析优先级
    priority = 2  # 默认为2
    case_level = case.get('用例等级', '').lower()
    if case_level == 'p0':
        priority = 1
    elif case_level == 'p1':
        priority = 2
    elif case_level == 'p2':
        priority = 3
    
    print(f"正在创建用例 [{row_number}/6]: {case_name}")
    
    # 调用创建用例API
    result = client.create_case(
        name=case_name,
        directory_id=target_directory_id,
        description=case_description,
        note=case_note,
        priority=priority
    )
    
    # 记录结果
    result_entry = {
        "row_number": row_number,
        "case_name": case_name,
        "case_id": result.get('data') if result.get('success') else None,
        "success": result.get('success', False),
        "message": result.get('message', '')
    }
    
    results.append(result_entry)
    
    if result.get('success'):
        success_count += 1
        print(f"  [OK] 创建成功，case_id: {result.get('data')}")
    else:
        failed_count += 1
        print(f"  [FAIL] 创建失败: {result.get('message')}")

# 汇总结果
summary = {
    "total": len(cases),
    "success_count": success_count,
    "failed_count": failed_count,
    "results": results
}

# 保存结果到文件
with open('create_result.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"批量创建完成！")
print(f"总计: {summary['total']} 条用例")
print(f"成功: {summary['success_count']} 条")
print(f"失败: {summary['failed_count']} 条")
print(f"结果已保存到: ./create_result.json")
print('='*60)
print(json.dumps(summary, ensure_ascii=False, indent=2))
