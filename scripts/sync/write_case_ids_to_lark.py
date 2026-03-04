#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将自动化用例ID写入飞书表格的脚本序号列
修正版：正确的range格式
"""
import json
import sys
import re
import requests

# 配置
APP_ID = 'cli_a83faf50a228900e'
APP_SECRET = 'VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH'
LARK_URL = 'https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=dfa872'
BASE_URL = "https://open.feishu.cn/open-apis"

# 是否测试模式（只更新一条）
TEST_MODE = False

# 加载映射关系
with open('sandbox/workspace/case_id_mapping.json', 'r', encoding='utf-8') as f:
    mapping_data = json.load(f)

def get_access_token():
    """获取访问令牌"""
    url = f"{BASE_URL}/auth/v3/app_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") == 0:
        return result.get("app_access_token")
    else:
        raise Exception(f"获取access_token失败: {result.get('msg')}")

def parse_url(url):
    """解析飞书表格URL"""
    match = re.search(r'/sheets/([a-zA-Z0-9]+)', url)
    if not match:
        raise ValueError("无法从URL中提取spreadsheet_token")
    spreadsheet_token = match.group(1)

    match = re.search(r'sheet=([a-zA-Z0-9]+)', url)
    sheet_id = match.group(1) if match else None

    return spreadsheet_token, sheet_id

def get_sheet_data(spreadsheet_token, sheet_id, access_token):
    """获取表格数据"""
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    if result.get("code") == 0:
        return result.get("data", {}).get("valueRange", {}).get("values", [])
    else:
        raise Exception(f"获取表格数据失败: {result.get('msg')}")

def write_to_cell(spreadsheet_token, range_str, value, access_token):
    """
    写入数据到单个单元格
    range_str格式: sheet_id!A1:A1 (起始和结束单元格相同)
    """
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "valueRange": {
            "range": range_str,
            "values": [[value]]
        }
    }

    print(f"  请求URL: {url}")
    print(f"  Range: {range_str}")
    print(f"  Value: {value}")

    response = requests.put(url, headers=headers, json=payload)
    result = response.json()

    print(f"  响应: code={result.get('code')}, msg={result.get('msg')}")

    if result.get("code") == 0:
        return {"success": True}
    else:
        return {"success": False, "message": result.get("msg"), "code": result.get("code")}

def col_number_to_letter(col_num):
    """将列号转换为字母（A, B, C, ... Z, AA, AB, ...）"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(65 + col_num % 26) + result
        col_num //= 26
    return result

def find_column_index(headers, column_name):
    """查找列索引（从1开始）"""
    for i, header in enumerate(headers):
        if isinstance(header, str) and column_name in header:
            return i + 1
    return None

def main():
    """主函数"""
    try:
        print('='*80)
        print('将自动化用例ID写入飞书表格' + (' [测试模式]' if TEST_MODE else ' [批量模式]'))
        print('='*80)
        print()

        # 步骤1: 获取access_token
        print('步骤1: 获取访问令牌...')
        access_token = get_access_token()
        print('[OK] 成功')
        print()

        # 步骤2: 解析URL
        print('步骤2: 解析表格URL...')
        spreadsheet_token, sheet_id = parse_url(LARK_URL)
        print(f'  spreadsheet_token: {spreadsheet_token}')
        print(f'  sheet_id: {sheet_id}')
        print('[OK] 成功')
        print()

        # 步骤3: 获取表格数据
        print('步骤3: 读取表格数据...')
        data = get_sheet_data(spreadsheet_token, sheet_id, access_token)

        if not data or len(data) < 2:
            print('[错误] 表格数据为空')
            return 1

        print(f'[OK] 读取到 {len(data)} 行数据')

        # 步骤4: 查找列
        print('\n步骤4: 查找目标列...')
        headers = data[0]
        case_code_col = find_column_index(headers, '用例编号')
        script_no_col = find_column_index(headers, '脚本序号')

        if not case_code_col:
            print('[错误] 未找到"用例编号"列')
            return 1

        if not script_no_col:
            print('[错误] 未找到"脚本序号"列')
            return 1

        col_letter = col_number_to_letter(script_no_col)
        print(f'  用例编号列: {case_code_col} ({col_number_to_letter(case_code_col)})')
        print(f'  脚本序号列: {script_no_col} ({col_letter})')
        print('[OK] 成功')
        print()

        # 步骤5: 构建更新列表
        print('步骤5: 分析需要更新的记录...')
        updates = []
        mapping = mapping_data['mapping']

        for row_idx, row in enumerate(data[1:], start=2):
            if not row or len(row) < case_code_col:
                continue

            case_code = row[case_code_col - 1] if case_code_col <= len(row) else None

            if not case_code:
                continue

            # 查找对应的自动化用例ID
            auto_case_id = None
            for m in mapping:
                if m['manual_case_code'] == case_code:
                    auto_case_id = m['auto_case_id']
                    break

            if auto_case_id:
                current_script_no = row[script_no_col - 1] if script_no_col <= len(row) else None

                if not current_script_no or str(current_script_no).strip() == '':
                    updates.append({
                        'row': row_idx,
                        'case_code': case_code,
                        'script_no': auto_case_id
                    })

        print(f'  找到 {len(updates)} 条需要更新的记录')

        if not updates:
            print('\n[完成] 没有需要更新的记录')
            return 0

        # 测试模式：只更新第一条
        if TEST_MODE:
            print('\n[测试模式] 只更新第一条记录')
            updates = updates[:1]

        print()
        # 步骤6: 执行更新
        print('步骤6: 开始更新表格...')
        success_count = 0
        fail_count = 0
        errors = []

        for idx, update in enumerate(updates, 1):
            row_idx = update['row']
            case_code = update['case_code']
            script_no = update['script_no']

            print(f'\n[{idx}/{len(updates)}] 第{row_idx}行: {case_code} -> {script_no}')

            # 构建range格式: sheet_id!起始单元格:结束单元格
            # 例如: dfa872!R2:R2
            cell = f"{col_letter}{row_idx}"
            range_str = f"{sheet_id}!{cell}:{cell}"

            result = write_to_cell(spreadsheet_token, range_str, str(script_no), access_token)

            if result.get('success'):
                print(f'  [成功] 更新完成')
                success_count += 1
            else:
                error_msg = f"第{row_idx}行失败: {result.get('message')} (code: {result.get('code')})"
                print(f'  [失败] {error_msg}')
                errors.append(error_msg)
                fail_count += 1

        print()
        print('='*80)
        print('更新完成汇总')
        print('='*80)
        print(f'成功: {success_count}/{len(updates)}')
        print(f'失败: {fail_count}/{len(updates)}')

        if errors:
            print('\n错误详情:')
            for error in errors:
                print(f'  - {error}')

        if TEST_MODE and success_count > 0:
            print('\n[OK] 测试成功！')
            print('如需批量更新所有记录，请修改脚本中的 TEST_MODE = False')

        return 0 if fail_count == 0 else 1

    except Exception as e:
        print(f'\n[ERROR] 执行失败: {e}')
        import traceback
        traceback.print_exc()

        # 记录错误
        with open('sandbox/workspace/lark_write_errors.log', 'w', encoding='utf-8') as f:
            f.write(f'错误: {e}\n\n')
            f.write(traceback.format_exc())

        return 1

if __name__ == "__main__":
    sys.exit(main())
