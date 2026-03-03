#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析飞书最新数据，确定需要创建和删除的用例
"""
import json

# 加载最新数据
with open('sandbox/workspace/lark_latest_data.json', 'r', encoding='utf-8') as f:
    latest_data = json.load(f)

# 加载已创建的用例
with open('sandbox/workspace/batch_create_result_1772541732.json', 'r', encoding='utf-8') as f:
    created_cases = json.load(f)

print('='*80)
print('飞书最新数据分析')
print('='*80)

# 分类统计
manual_no_script = []  # 手工用例，无脚本序号，需要创建自动化
manual_with_script = []  # 手工用例，有脚本序号，已自动化

for case in latest_data:
    case_code = case.get('用例编号')
    case_name = case.get('用例名称')
    case_type = case.get('手工/自动化')
    script_no = case.get('脚本序号')

    # 判断脚本序号是否有效
    has_script = script_no and str(script_no).strip()

    if case_type == '手工':
        if has_script:
            manual_with_script.append({
                'case_code': case_code,
                'case_name': case_name,
                'script_no': str(script_no)
            })
        else:
            manual_no_script.append({
                'case_code': case_code,
                'case_name': case_name
            })

print(f'\n总用例数: {len(latest_data)}')
print(f'手工用例（无脚本序号，需要创建自动化）: {len(manual_no_script)}')
print(f'手工用例（有脚本序号，已自动化）: {len(manual_with_script)}')
print(f'已创建自动化用例: {len(created_cases)}')

# 输出需要创建的用例
print('\n' + '='*80)
print('需要创建自动化的手工用例（共{}个）'.format(len(manual_no_script)))
print('='*80)
for i, case in enumerate(manual_no_script, 1):
    print(f'{i}. [{case["case_code"]}] {case["case_name"]}')

# 输出已有脚本的用例
print('\n' + '='*80)
print('已有脚本序号的手工用例（共{}个，不需要创建）'.format(len(manual_with_script)))
print('='*80)
for i, case in enumerate(manual_with_script, 1):
    print(f'{i}. [{case["case_code"]}] {case["case_name"]} - 脚本序号: {case["script_no"]}')

# 找出需要删除的已创建用例
print('\n' + '='*80)
print('对比分析')
print('='*80)

# 已创建的用例编号
created_codes = {c['manual_case_code'] for c in created_cases}

# 需要创建的用例编号
need_create_codes = {c['case_code'] for c in manual_no_script}

# 需要删除的用例（已创建但不在需要创建列表中）
to_delete = []
for created in created_cases:
    if created['manual_case_code'] not in need_create_codes:
        to_delete.append(created)

print(f'\n需要删除的已创建用例: {len(to_delete)}个')
if to_delete:
    print('删除列表:')
    for i, case in enumerate(to_delete, 1):
        print(f'  {i}. [{case["manual_case_code"]}] {case["manual_case_name"]} - 自动化用例ID: {case["auto_case_id"]}')

# 需要保留的用例
to_keep = []
for created in created_cases:
    if created['manual_case_code'] in need_create_codes:
        to_keep.append(created)

print(f'\n需要保留的已创建用例: {len(to_keep)}个')
print(f'需要新创建的用例: {len(manual_no_script) - len(to_keep)}个')

# 保存结果
result = {
    'need_create': manual_no_script,
    'has_script': manual_with_script,
    'to_delete': to_delete,
    'to_keep': to_keep
}

with open('sandbox/workspace/case_creation_plan.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'\n结果已保存到: sandbox/workspace/case_creation_plan.json')
