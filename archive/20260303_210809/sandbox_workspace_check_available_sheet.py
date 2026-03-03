import requests

# 尝试读取表格 - 使用已知可以访问的token
spreadsheet_token = "K8V2sTKLyhE54Ot75EycbnKLnvb"
sheet_id = "FYZ5JP"

# 先获取token
token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
headers = {"Content-Type": "application/json"}
data = {"app_id": "cli_a83faf50a228900e", "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"}

response = requests.post(token_url, headers=headers, json=data)
result = response.json()
print(f"Token获取成功")

access_token = result.get("app_access_token")

# 尝试读取表格
read_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(read_url, headers=headers)
result = response.json()
values = result.get("data", {}).get("valueRange", {}).get("values", [])

print(f"\n读取成功! 共 {len(values)} 行")

if values:
    headers = values[0]
    print(f"\n表头字段 ({len(headers)} 个):")
    for i, h in enumerate(headers):
        print(f"  {i}: {h}")

    # 查找包含"无感接入类型为仅无线，用户进行有线认证"的行
    print(f"\n搜索匹配的用例...")
    for i, row in enumerate(values[1:], start=2):  # 从第2行开始
        if len(row) > 0:
            # 查找用例名称列
            case_name = row[6] if len(row) > 6 else ""  # 根据之前的经验，用例名称在第6列
            if case_name and "有线认证" in case_name:
                print(f"  行 {i}: {case_name}")
