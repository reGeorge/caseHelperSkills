import json
import os

# 设置工作目录
base_dir = r'd:/Code/caseHelper/sandbox/workspace'
os.chdir(base_dir)

# 读取输入文件
with open('test_cases_with_script_info.json', 'r', encoding='utf-8') as f:
    all_cases = json.load(f)

print(f'总用例数: {len(all_cases)}')

# 定义筛选关键词
keywords = ['用户进行有线认证', '有线portal认证', '有线1x认证', '有线MAB认证']

# 筛选符合条件的用例
filtered_cases = []
for idx, case in enumerate(all_cases, 1):
    case_name = case.get('用例名称', '')
    case_desc = case.get('用例描述', '')
    
    # 检查是否包含任一关键词
    matches = []
    for keyword in keywords:
        if keyword.lower() in case_name.lower() or keyword.lower() in case_desc.lower():
            matches.append(keyword)
    
    if matches:
        # 添加标记
        case['是否可自动化'] = '是'
        filtered_cases.append({
            'row_number': idx,
            'case_name': case_name,
            'matched_keywords': matches,
            'data': case
        })

print(f'符合条件的用例数: {len(filtered_cases)}')
print('\n筛选结果详情:')
for item in filtered_cases:
    print(f'行号: {item["row_number"]} | 用例名称: {item["case_name"]} | 匹配关键词: {item["matched_keywords"]}')

# 保存筛选结果（只保留原始数据，不包含辅助字段）
output_data = [item['data'] for item in filtered_cases]
with open('wired_auth_cases.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f'\n筛选结果已保存到 wired_auth_cases.json')
print(f'共保存 {len(output_data)} 条用例')
