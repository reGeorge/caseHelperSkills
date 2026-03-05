#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量回写 802.1x密码复杂度用例分析结果到飞书表格
新增列: K=是否可自动化 / L=不可自动化原因 / M=脚本名称
"""
import sys, os, json, requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-writer'))
from lark_sheet_writer import LarkSheetWriter

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "UmATpA"
BASE_URL = "https://open.feishu.cn/open-apis"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')


def put_range(token, range_str, values):
    """使用 PUT 更新已有单元格"""
    url = BASE_URL + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    body = {'valueRange': {'range': range_str, 'values': values}}
    r = requests.put(url, headers=headers, json=body)
    result = r.json()
    return result.get('code') == 0, result.get('msg', '')


def main():
    result_file = os.path.join(WORKSPACE, 'dot1x_passwd_analysis_result.json')
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    writer = LarkSheetWriter(APP_ID, APP_SECRET)
    access_token = writer.get_access_token()
    print(f"Token获取成功，共 {len(results)} 条待写入")

    end_row = len(results) + 1  # 数据从第2行开始

    # 写 K1 表头
    ok, msg = put_range(access_token, SHEET_ID + '!K1:K1', [['是否可自动化']])
    print(f"是否可自动化表头(K1): {'✅' if ok else '❌ ' + msg}")

    # 写 K列: 是否可自动化
    col_k = [[r['是否可自动化']] for r in results]
    ok, msg = put_range(access_token, SHEET_ID + '!K2:K' + str(end_row), col_k)
    print(f"是否可自动化(K): {'✅' if ok else '❌ ' + msg}")

    # 写 L1 表头
    ok, msg = put_range(access_token, SHEET_ID + '!L1:L1', [['不可自动化原因']])
    print(f"不可自动化原因表头(L1): {'✅' if ok else '❌ ' + msg}")

    # 写 L列: 不可自动化原因
    col_l = [[r.get('不可自动化原因', '')] for r in results]
    ok, msg = put_range(access_token, SHEET_ID + '!L2:L' + str(end_row), col_l)
    print(f"不可自动化原因(L): {'✅' if ok else '❌ ' + msg}")

    # 写 M1 表头
    ok, msg = put_range(access_token, SHEET_ID + '!M1:M1', [['脚本名称']])
    print(f"脚本名称表头(M1): {'✅' if ok else '❌ ' + msg}")

    # 写 M列: 脚本名称
    col_m = [[r['脚本名称']] for r in results]
    ok, msg = put_range(access_token, SHEET_ID + '!M2:M' + str(end_row), col_m)
    print(f"脚本名称(M): {'✅' if ok else '❌ ' + msg}")

    print("✅ 回写完成")


if __name__ == "__main__":
    main()
