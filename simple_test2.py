import requests
print("开始...")

token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
token_data = {"app_id": "cli_a83faf50a228900e", "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"}

r = requests.post(token_url, json=token_data)
result = r.json()
print(f"Token响应: {result}")

if result.get("code") == 0:
    token = result.get("app_access_token")
    print(f"Token: {token[:20]}...")
    
    # 写入 - 尝试使用v3 API
    write_url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/K8V2sTKLyhE54Ot75EycbnKLnvb/values/write"
    write_data = {"range": "FYZ5JP!P60", "values": [["66249"]]}
    
    wr = requests.post(write_url, headers={"Authorization": f"Bearer {token}"}, json=write_data)
    print(f"写入状态码: {wr.status_code}")
    print(f"写入响应头: {wr.headers}")
    print(f"写入响应文本: {wr.text}")
    try:
        write_result = wr.json()
        print(f"写入响应JSON: {write_result}")
    except Exception as e:
        print(f"JSON解析失败: {e}")
else:
    print("获取Token失败")
