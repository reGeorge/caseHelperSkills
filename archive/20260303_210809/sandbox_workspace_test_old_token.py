import requests

# 尝试读取表格 - 使用之前的token
spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
sheet_id = "FYZ5JP"

# 先获取token
token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
headers = {"Content-Type": "application/json"}
data = {"app_id": "cli_a83faf50a228900e", "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"}

response = requests.post(token_url, headers=headers, json=data)
result = response.json()
print(f"Token响应: {result}")

if result.get("code") == 0:
    access_token = result.get("app_access_token")
    print(f"Token获取成功")

    # 尝试读取表格
    read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    print(f"\n尝试读取表格: {read_url}")
    response = requests.get(read_url, headers=headers)
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        values = result.get("data", {}).get("valueRange", {}).get("values", [])
        print(f"读取成功! 共 {len(values)} 行")
        if values:
            print(f"表头: {values[0][:3]}...")
    else:
        print(f"响应内容: {response.text[:500]}")
else:
    print(f"Token获取失败: {result.get('msg')}")
