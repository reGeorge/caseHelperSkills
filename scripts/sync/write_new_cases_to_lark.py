#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将新创建的13个自动化用例ID写入飞书表格
"""

import sys
import os
import json
import time
import requests

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 飞书API配置
APP_ID = 'cli_a83faf50a228900e'
APP_SECRET = 'VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH'
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "dfa872"

# 列映射
SCRIPT_NAME_COL = 17  # Q列 - 脚本名称
SCRIPT_ID_COL = 18    # R列 - 脚本序号

def get_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("app_access_token")
            else:
                print(f"获取token失败: code={data.get('code')}, msg={data.get('msg')}")
        else:
            print(f"HTTP错误: {resp.status_code}")
        return None
    except Exception as e:
        print(f"获取token异常: {e}")
        return None

def write_to_cell(token, range_str, value):
    """写入单元格"""
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "valueRange": {
            "range": range_str,
            "values": [[value]]
        }
    }
    
    try:
        resp = requests.put(url, headers=headers, json=payload, timeout=30)
        print(f"    请求URL: {url}")
        print(f"    Range: {range_str}, Value: {str(value)[:50]}")
        print(f"    响应状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"    响应内容: code={data.get('code')}, msg={data.get('msg')}")
            if data.get("code") == 0:
                return True
            else:
                print(f"  [ERROR] 写入失败: {data.get('msg')}")
                return False
        else:
            print(f"  [ERROR] HTTP错误: {resp.status_code}")
            print(f"  [ERROR] 响应内容: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # 读取创建结果
    print("读取创建结果...")
    with open('sandbox/workspace/creation_result_1772604609.json', encoding='utf-8') as f:
        creation_result = json.load(f)
    
    # 读取飞书数据获取行号
    print("读取飞书数据...")
    with open('sandbox/workspace/lark_latest_data.json', encoding='utf-8') as f:
        lark_data = json.load(f)
    
    # 构建用例编号到行号的映射
    case_to_row = {}
    for i, case in enumerate(lark_data):
        case_number_full = case.get('用例编号', '')
        if case_number_full:
            # 提取TP编号 (如: RG-UNC-无感认证设置-TP-001 -> TP-001)
            if 'TP-' in case_number_full:
                tp_number = 'TP-' + case_number_full.split('TP-')[1]
                # 飞书表格从第2行开始（第1行是表头）
                case_to_row[tp_number] = i + 2
    
    print(f"找到 {len(case_to_row)} 个用例的行号映射")
    print()
    
    # 获取token
    print("获取飞书访问令牌...")
    token = get_access_token()
    
    if not token:
        print("[ERROR] 无法获取访问令牌")
        return 1
    
    print("[OK] 获取成功")
    print()
    
    # 写入新创建的用例
    print("=" * 80)
    print("开始写入飞书表格")
    print("=" * 80)
    
    new_cases = creation_result["cases"]
    print(f"\n待写入用例数: {len(new_cases)}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for case_info in new_cases:
        case_number = case_info["case_number"]
        case_id = case_info["case_id"]
        case_name = case_info["case_name"]
        
        # 获取行号
        row = case_to_row.get(case_number)
        if not row:
            print(f"[SKIP] {case_number} - 未找到行号映射")
            continue
        
        print(f"写入 {case_number} (行{row}):")
        print(f"  脚本名称: {case_name[:40]}...")
        print(f"  脚本序号: {case_id}")
        
        # 写入脚本名称 (Q列)
        range_name = f"{SHEET_ID}!Q{row}:Q{row}"
        if write_to_cell(token, range_name, case_name):
            print(f"  [OK] 脚本名称写入成功")
        else:
            print(f"  [ERROR] 脚本名称写入失败")
            fail_count += 1
            time.sleep(0.3)
            continue
        
        time.sleep(0.2)
        
        # 写入脚本序号 (R列)
        range_id = f"{SHEET_ID}!R{row}:R{row}"
        if write_to_cell(token, range_id, case_id):
            print(f"  [OK] 脚本序号写入成功")
            success_count += 1
        else:
            print(f"  [ERROR] 脚本序号写入失败")
            fail_count += 1
        
        time.sleep(0.3)
    
    print()
    print("=" * 80)
    print("写入完成")
    print("=" * 80)
    print(f"\n统计:")
    print(f"  成功数量: {success_count}")
    print(f"  失败数量: {fail_count}")
    print(f"  总计: {len(new_cases)}")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
