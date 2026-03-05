#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 W9QybU 分析结果回写到飞书表格
写 J=是否可自动化  K=不可自动化原因  L=脚本名称
"""

import sys
import os
import json
import requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))

from lark_sheet_reader import LarkSheetReader

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "W9QybU"
BASE_URL = "https://open.feishu.cn/open-apis"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')

COL_AUTO     = 'J'   # 是否可自动化
COL_REASON   = 'K'   # 不可自动化原因
COL_SCRIPT   = 'L'   # 脚本名称


def get_token():
    reader = LarkSheetReader(APP_ID, APP_SECRET)
    return reader.get_access_token()


def put_range(access_token, range_str, values):
    url = BASE_URL + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
    }
    payload = {
        'valueRange': {
            'range': range_str,
            'values': values,
        }
    }
    resp = requests.put(url, headers=headers, json=payload)
    return resp.json()


def main():
    result_file = os.path.join(WORKSPACE, 'w9qybu_analysis_result.json')
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f"📂 载入 {len(results)} 条分析结果")

    token = get_token()
    print("🔑 获取 Token 成功")

    # ── 写表头（第1行）──
    head_range = f"{SHEET_ID}!{COL_AUTO}1:{COL_SCRIPT}1"
    rv = put_range(token, head_range, [['是否可自动化', '不可自动化原因', '脚本名称']])
    print(f"  写表头: {rv.get('code')} {rv.get('msg','')}")

    start_row = 2
    end_row   = start_row + len(results) - 1
    data_range = f"{SHEET_ID}!{COL_AUTO}{start_row}:{COL_SCRIPT}{end_row}"
    values = [
        [
            r['是否可自动化'],
            r['不可自动化原因'],
            r['脚本名称'],
        ]
        for r in results
    ]

    rv = put_range(token, data_range, values)
    print(f"  写数据 {start_row}:{end_row} → code={rv.get('code')} {rv.get('msg','')}")

    if rv.get('code') == 0:
        print(f"\n✅ 回写完成！共写入 {len(results)} 行 (J/K/L 列)")
    else:
        print(f"\n❌ 回写失败: {json.dumps(rv, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
