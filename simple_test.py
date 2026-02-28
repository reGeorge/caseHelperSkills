# -*- coding: utf-8 -*-
import requests
import json

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": "cli_a2bd4735a538900d", "app_secret": "fG9s9Jt2YbUZq7lXnE3jK0mM7pP5hH4b"}
    r = requests.post(url, json=data)
    result = r.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    return None

def read_range(token, spreadsheet_token, range_str):
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    result = r.json()
    if result.get("code") == 0:
        return result.get("data", {}).get("valueRange", {}).get("values", [])
    return None

def write_range(token, spreadsheet_token, range_str, values):
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
    data = {"valueRange": {"values": values}}
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=data)
    result = r.json()
    print(f"写入响应: {json.dumps(result, ensure_ascii=False)}")
    return result.get("code") == 0

token = get_feishu_token()
if token:
    spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
    
    print("读取P60...")
    values = read_range(token, spreadsheet_token, "FYZ5JP!P60")
    print(f"当前值: {values}")
    
    print("\n写入P60...")
    success = write_range(token, spreadsheet_token, "FYZ5JP!P60", [["66249"]])
    print(f"写入结果: {'成功' if success else '失败'}")
    
    print("\n再次读取P60...")
    values = read_range(token, spreadsheet_token, "FYZ5JP!P60")
    print(f"当前值: {values}")
