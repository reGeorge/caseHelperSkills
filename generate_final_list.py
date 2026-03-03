#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成最终需要创建的用例清单
"""
import json

# 加载分析结果
with open('sandbox/workspace/case_creation_plan.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

print('='*80)
print('最终需要创建的15个自动化用例清单')
print('='*80)
print()

need_create = plan['need_create']
to_keep = plan['to_keep']

print(f'需要创建: {len(need_create)}个')
print(f'已正确创建: {len(to_keep)}个')
print()

# 匹配已创建的用例
print('已创建的用例映射:')
print('-'*80)
for i, case in enumerate(need_create, 1):
    # 查找对应的已创建用例
    created = None
    for c in to_keep:
        if c['manual_case_code'] == case['case_code']:
            created = c
            break

    if created:
        print(f'{i}. [{case["case_code"]}] {case["case_name"]}')
        print(f'   -> 自动化用例ID: {created["auto_case_id"]}')
    else:
        print(f'{i}. [{case["case_code"]}] {case["case_name"]}')
        print(f'   -> 需要创建')

print()
print('='*80)
print('已有自动化的13个用例（跳过，不创建）')
print('='*80)
print()

has_script = plan['has_script']
for i, case in enumerate(has_script, 1):
    print(f'{i}. [{case["case_code"]}] {case["case_name"]}')
    print(f'   -> 已有脚本序号: {case["script_no"]}')

# 生成报告
report = {
    'summary': {
        'total_manual_cases': 28,
        'need_create_count': 15,
        'has_script_count': 13,
        'created_correctly': len(to_keep),
        'created_duplicates': 13
    },
    'need_create': need_create,
    'has_script': has_script,
    'created_correctly': to_keep
}

with open('sandbox/workspace/final_case_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print()
print(f'详细报告已保存到: sandbox/workspace/final_case_report.json')
