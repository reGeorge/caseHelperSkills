import requests
import json

# 表格token
spreadsheet_token = "OXndwZNS9i6hhjk16VwcRai5ngd"

# 尝试不同的API端点
endpoints = [
    f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query",
    f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets",
    f"https://open.feishu.cn/open-apis/sheets/v4/spreadsheets/{spreadsheet_token}/sheets/query",
]

# 使用获取到的access_token
access_token = "t-g1042se4MVU44RPWOUNWASDXKT2WCV7Y5PM2G7R6"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for i, url in enumerate(endpoints, 1):
    print(f"\n尝试端点 {i}: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("code") == 0:
                    sheets = data.get("data", {}).get("sheets", [])
                    print(f"\n✓ 成功获取工作表列表！")
                    print(f"工作表数量: {len(sheets)}")
                    print("-" * 60)
                    for sheet in sheets:
                        sheet_id = sheet.get('sheet_id')
                        title = sheet.get('title')
                        print(f"Sheet ID: {sheet_id}")
                        print(f"Sheet 名称: {title}")
                        print("-" * 60)
                    break
                else:
                    print(f"API调用失败: {data.get('msg')}")
                    print(f"错误码: {data.get('code')}")
            except json.JSONDecodeError:
                print("响应不是有效的JSON格式")
        elif response.status_code == 403:
            print("权限不足，请检查应用权限设置")
        elif response.status_code == 404:
            print("表格不存在或token不正确")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
