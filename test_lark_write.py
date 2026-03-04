#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试飞书API写入
"""
import requests

APP_ID = "cli_a539f7a6b4f8d00c"
APP_SECRET = "rOPL8VJJHLbVn7dVRvq0PhV5tCvxRf3Y"

print("Step 1: 获取access_token...")
url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
resp = requests.post(url, json={
    "app_id": APP_ID,
    "app_secret": APP_SECRET
}, timeout=30)

print(f"状态码: {resp.status_code}")
print(f"响应: {resp.json()}")

data = resp.json()
if data.get("code") == 0:
    token = data.get("app_access_token")
    print(f"Token: {token[:20]}...")
else:
    print(f"获取token失败: {data}")
    exit(1)

print("\nStep 2: 测试写入...")
spreadsheet_token = "Mw7escaVhh92SSts8incmbbUnkc"
sheet_id = "dfa872"
range_str = f"{sheet_id}!Q2:Q2"

write_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "valueRange": {
        "range": range_str,
        "values": [["测试写入"]]
    }
}

print(f"URL: {write_url}")
print(f"Range: {range_str}")
print(f"Payload: {payload}")

resp = requests.put(write_url, headers=headers, json=payload, timeout=30)
print(f"\n状态码: {resp.status_code}")
print(f"响应: {resp.json()}")

if resp.json().get("code") == 0:
    print("\n[SUCCESS] 写入成功！")
else:
    print(f"\n[FAILED] 写入失败")
