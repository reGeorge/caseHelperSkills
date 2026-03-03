#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析手工用例，筛选出需要创建自动化的用例
"""

import json

# 加载数据
with open('sandbox/workspace/test_cases_with_script_info.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'总用例数: {len(data)}\n')

# 分类统计
manual_no_script = []  # 手工用例，无脚本序号，需要创建自动化
manual_with_script = []  # 手工用例，有脚本序号，已自动化
auto_cases = []  # 已自动化用例

for case in data:
    case_type = case.get('手工/自动化')
    script_no = case.get('脚本序号')
    
    # 判断脚本序号是否有效（非空且非None）
    has_script = script_no and str(script_no).strip()
    
    if case_type == '手工':
        if has_script:
            manual_with_script.append(case)
        else:
            manual_no_script.append(case)
    elif case_type == '自动化':
        auto_cases.append(case)

print(f'手工用例（无脚本序号，需要创建自动化）: {len(manual_no_script)}')
print(f'手工用例（有脚本序号，已自动化）: {len(manual_with_script)}')
print(f'已自动化用例: {len(auto_cases)}')
print()

print('='*80)
print('需要创建自动化的手工用例列表:')
print('='*80)
for i, case in enumerate(manual_no_script, 1):
    print(f'{i}. [{case.get("用例编号")}] {case.get("用例名称")}')

print()
print('='*80)
print('已有脚本序号的手工用例（不需要创建）:')
print('='*80)
for i, case in enumerate(manual_with_script, 1):
    print(f'{i}. [{case.get("用例编号")}] {case.get("用例名称")} - 脚本序号: {case.get("脚本序号")}')

# 保存需要创建的用例列表
if manual_no_script:
    output_file = 'sandbox/workspace/manual_cases_need_automation.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manual_no_script, f, ensure_ascii=False, indent=2)
    print(f'\n需要创建自动化的用例已保存到: {output_file}')
