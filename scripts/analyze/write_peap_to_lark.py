#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量回写 PEAP 分析结果到飞书表格（使用 PUT 更新已有单元格）
列映射: A=用例编号, G=是否可自动化, I=脚本名称, J=不可自动化原因
"""
import sys, os, json, requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-writer'))
from lark_sheet_writer import LarkSheetWriter

LARK_APP_ID = "cli_a83faf50a228900e"
LARK_APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "gBtCcn"
BASE_URL = "https://open.feishu.cn/open-apis"


def put_range(token, range_str, values):
    """使用 PUT 方法更新已有单元格"""
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "valueRange": {
            "range": range_str,
            "values": values
        }
    }
    resp = requests.put(url, headers=headers, json=body)
    result = resp.json()
    return result.get("code") == 0, result.get("msg", "")


def main():
    with open(os.path.join(project_root, 'sandbox', 'workspace', 'peap_analysis_result.json'), 'r', encoding='utf-8') as f:
        results = json.load(f)

    writer = LarkSheetWriter(LARK_APP_ID, LARK_APP_SECRET)
    access_token = writer.get_access_token()
    print(f"Token获取成功, 共 {len(results)} 条待写入")

    end_row = len(results) + 1

    # 批量写 用例编号 (A列)
    col_a = [[r['用例编号']] for r in results]
    ok, msg = put_range(access_token, f"{SHEET_ID}!A2:A{end_row}", col_a)
    print(f"用例编号(A): {'✅' if ok else '❌ ' + msg}")

    # 批量写 是否可自动化 (G列)
    col_g = [[r['是否可自动化']] for r in results]
    ok, msg = put_range(access_token, f"{SHEET_ID}!G2:G{end_row}", col_g)
    print(f"是否可自动化(G): {'✅' if ok else '❌ ' + msg}")

    # 批量写 脚本名称 (I列)
    col_i = [[r['脚本名称']] for r in results]
    ok, msg = put_range(access_token, f"{SHEET_ID}!I2:I{end_row}", col_i)
    print(f"脚本名称(I): {'✅' if ok else '❌ ' + msg}")

    # 写 不可自动化原因 表头 (J1)
    ok, msg = put_range(access_token, f"{SHEET_ID}!J1:J1", [["不可自动化原因"]])
    print(f"不可自动化原因表头(J1): {'✅' if ok else '❌ ' + msg}")

    # 批量写 不可自动化原因 (J列)
    col_j = [[r.get('不可自动化原因', '')] for r in results]
    ok, msg = put_range(access_token, f"{SHEET_ID}!J2:J{end_row}", col_j)
    print(f"不可自动化原因(J): {'✅' if ok else '❌ ' + msg}")

    print("✅ 回写完成")

if __name__ == "__main__":
    main()
