#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
读取飞书表格最新数据
"""
import sys
import os
import json
import re
import requests

def read_lark_sheet(url: str, app_id: str, app_secret: str) -> list:
    """读取飞书表格"""
    # 解析URL
    match = re.search(r'/sheets/([a-zA-Z0-9]+)', url)
    if not match:
        raise ValueError("无法从URL中提取spreadsheet_token")
    spreadsheet_token = match.group(1)
    
    match = re.search(r'sheet=([a-zA-Z0-9]+)', url)
    sheet_id = match.group(1) if match else None
    
    # 获取access_token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}
    
    response = requests.post(token_url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    access_token = result.get("app_access_token")
    
    if not access_token:
        raise ValueError("获取access_token失败")
    
    # 如果没有sheet_id，获取第一个sheet
    if not sheet_id:
        query_url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.get(query_url, headers=headers)
        response.raise_for_status()
        result = response.json()
        sheets = result.get("data", {}).get("sheets", [])
        if sheets:
            sheet_id = sheets[0].get("sheet_id")
        else:
            raise ValueError("未找到任何sheet")
    
    # 读取数据
    read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.get(read_url, headers=headers)
    response.raise_for_status()
    result = response.json()
    values = result.get("data", {}).get("valueRange", {}).get("values", [])
    
    # 转换为字典列表
    if not values or len(values) < 2:
        return []
    
    headers_row = values[0]
    result_data = []
    
    for row in values[1:]:
        if not any(row):
            continue
        
        row_dict = {}
        for i, cell in enumerate(row):
            if i < len(headers_row):
                key = headers_row[i]
                # 处理key的复杂类型
                if isinstance(key, (dict, list)):
                    key = json.dumps(key, ensure_ascii=False)
                # 处理value的复杂类型
                if isinstance(cell, (dict, list)):
                    cell = json.dumps(cell, ensure_ascii=False)
                row_dict[key] = cell if cell else None
        
        result_data.append(row_dict)
    
    return result_data


def main():
    """主函数"""
    # 配置
    app_id = 'cli_a83faf50a228900e'
    app_secret = 'VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH'
    url = "https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=dfa872"
    output = "sandbox/workspace/lark_latest_data.json"
    
    try:
        print("=" * 80)
        print("读取飞书表格最新数据")
        print("=" * 80)
        print(f"表格URL: {url}")
        print("-" * 80)
        
        # 读取表格
        print("\n正在读取表格...")
        data = read_lark_sheet(url, app_id, app_secret)
        
        print(f"成功读取 {len(data)} 行数据")
        
        # 保存到文件
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到: {output}")
        
        # 分析数据
        print("\n" + "=" * 80)
        print("数据分析")
        print("=" * 80)
        
        manual_no_script = []
        manual_with_script = []
        auto_cases = []
        
        for case in data:
            case_type = case.get('手工/自动化')
            script_no = case.get('脚本序号')
            
            # 判断脚本序号是否有效
            has_script = script_no and str(script_no).strip()
            
            if case_type == '手工':
                if has_script:
                    manual_with_script.append(case)
                else:
                    manual_no_script.append(case)
            elif case_type == '自动化':
                auto_cases.append(case)
        
        print(f"总用例数: {len(data)}")
        print(f"手工用例（无脚本序号，需要创建自动化）: {len(manual_no_script)}")
        print(f"手工用例（有脚本序号，已自动化）: {len(manual_with_script)}")
        print(f"已自动化用例: {len(auto_cases)}")
        
        if manual_with_script:
            print("\n已有脚本序号的手工用例:")
            for i, case in enumerate(manual_with_script, 1):
                print(f"  {i}. [{case.get('用例编号')}] {case.get('用例名称')[:50]}... - 脚本序号: {case.get('脚本序号')}")
        
        print("\n[OK] 读取完成")
        return 0
        
    except Exception as e:
        print(f"\n[错误] 读取失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
