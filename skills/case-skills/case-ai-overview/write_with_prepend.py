#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用飞书 values_prepend API 将 AI 概述写入到"脚本名称"列
"""

import requests
import json
import sys

def write_with_prepend(spreadsheet_token: str, sheet_id: str, access_token: str, overviews: list):
    """
    使用 values_prepend API 写入数据到指定列
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_prepend"

    # 构建数据 - 每行数据为一个数组，AI概述作为第一个元素
    values = [[overview] for overview in overviews]

    # 写入到 K 列（第 11 列），从 K2 开始
    data = {
        "valueRange": {
            "range": f"{sheet_id}!K2:K101",
            "values": values
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    print(f"正在写入 {len(values)} 条数据...")
    print(f"范围: {data['valueRange']['range']}")
    print("-" * 80)

    print(f"请求 URL: {url}")
    print(f"请求体: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
    print("-" * 80)

    response = requests.post(url, headers=headers, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print("-" * 80)

    result = response.json()

    if result.get("code") != 0:
        print(f"错误代码: {result.get('code')}")
        print(f"错误信息: {result.get('msg')}")
        if 'error' in result:
            print(f"详细信息: {result['error']}")
        raise Exception(f"写入表格失败")

    print(f"成功写入 {len(values)} 条数据")
    print("-" * 80)
    return result

def main():
    if len(sys.argv) < 3:
        print("用法: python write_with_prepend.py <access_token> <json_file>")
        sys.exit(1)

    access_token = sys.argv[1]
    spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
    sheet_id = "FYZ5JP"
    json_file = sys.argv[2]

    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    # 提取 AI 概述
    overviews = [case.get("用例AI概述", "") for case in cases]

    print(f"准备写入 {len(overviews)} 条 AI 概述到'脚本名称'列")
    print("-" * 80)

    # 写入数据
    write_with_prepend(spreadsheet_token, sheet_id, access_token, overviews)

    print("[OK] 写入完成！")

if __name__ == "__main__":
    main()
