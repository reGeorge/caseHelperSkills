#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成新增的15条用例ID与飞书文档的映射关系
"""
import json

# 加载最终报告
with open('sandbox/workspace/final_case_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

print('='*80)
print('新增的15条自动化用例ID与飞书文档映射关系')
print('='*80)
print()

need_create = report['need_create']
created_correctly = report['created_correctly']

# 创建映射关系
mapping = []
for i, case in enumerate(need_create, 1):
    # 查找对应的已创建用例
    auto_case_id = None
    for c in created_correctly:
        if c['manual_case_code'] == case['case_code']:
            auto_case_id = c['auto_case_id']
            break

    mapping.append({
        'seq': i,
        'manual_case_code': case['case_code'],
        'manual_case_name': case['case_name'],
        'auto_case_id': auto_case_id
    })

# 输出表格
print(f'{"序号":<6} {"手工用例编号":<30} {"自动化用例ID":<15} {"用例名称"}')
print('-'*80)
for m in mapping:
    # 截取用例名称（太长）
    name = m['manual_case_name']
    if len(name) > 40:
        name = name[:40] + '...'
    print(f'{m["seq"]:<6} {m["manual_case_code"]:<30} {m["auto_case_id"]:<15} {name}')

# 输出用例ID列表
print()
print('='*80)
print('自动化用例ID列表（共15个）')
print('='*80)
auto_case_ids = [m['auto_case_id'] for m in mapping]
print(', '.join(auto_case_ids))

# 生成Markdown表格
print()
print('='*80)
print('Markdown表格格式')
print('='*80)
print()
print('| 序号 | 手工用例编号 | 自动化用例ID | 用例名称 | 飞书文档链接 |')
print('|------|-------------|-------------|----------|-------------|')
for m in mapping:
    name = m['manual_case_name']
    if len(name) > 50:
        name = name[:50] + '...'
    # 飞书文档链接（假设用例编号可以作为锚点）
    lark_url = f'https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=dfa872'
    print(f'| {m["seq"]} | {m["manual_case_code"]} | {m["auto_case_id"]} | {name} | [查看]({lark_url}) |')

# 保存为JSON
output = {
    'total': 15,
    'mapping': mapping,
    'auto_case_ids': auto_case_ids
}

with open('sandbox/workspace/case_id_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print(f'映射关系已保存到: sandbox/workspace/case_id_mapping.json')
