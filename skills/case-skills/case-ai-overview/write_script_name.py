#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用飞书 API 将 AI 概述写入到"脚本名称"列
"""

import requests
import json
import sys

def get_access_token(app_id: str, app_secret: str) -> str:
    """获取访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"获取 access_token 失败: {result}")

    return result.get("tenant_access_token")

def write_to_sheet_column(spreadsheet_token: str, sheet_id: str, access_token: str, overviews: list):
    """
    将 AI 概述写入到"脚本名称"列（第 11 列，即 K 列）
    使用 batch_update API 进行批量更新
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"

    # K 列对应索引 10（从 0 开始）
    # 从第 2 行开始（第 1 行是标题）
    start_row = 2
    column_index = 10

    # 构建更新数据
    # values 格式: [row_index][column_index] = value
    values = {}
    for i, overview in enumerate(overviews, start=start_row):
        # row_index 是从 0 开始的，所以第 2 行是索引 1
        row_idx = i - 1
        if row_idx not in values:
            values[row_idx] = {}
        values[row_idx][column_index] = overview

    # 构建请求体
    data = {
        "valueRange": {
            "range": f"{sheet_id}!K2:K{len(overviews) + 1}",
            "values": [[overview] for overview in overviews]
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 使用 values API 写入数据
    response = requests.put(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"写入表格失败: {result}")

    print(f"成功写入 {len(overviews)} 条数据")
    return result

def main():
    if len(sys.argv) < 4:
        print("用法: python write_script_name.py <app_id> <app_secret> <json_file>")
        sys.exit(1)

    app_id = sys.argv[1]
    app_secret = sys.argv[2]
    spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
    sheet_id = "FYZ5JP"
    json_file = sys.argv[3]

    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    # 提取 AI 概述
    overviews = [case.get("用例AI概述", "") for case in cases]

    print(f"准备写入 {len(overviews)} 条 AI 概述到'脚本名称'列")
    print("-" * 80)

    # 获取访问令牌
    print("获取访问令牌...")
    access_token = get_access_token(app_id, app_secret)

    # 写入数据
    print("写入数据...")
    write_to_sheet_column(spreadsheet_token, sheet_id, access_token, overviews)

    print("-" * 80)
    print("[OK] 写入完成！")

if __name__ == "__main__":
    main()
