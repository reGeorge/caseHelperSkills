import requests
import json
import os
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

# 飞书API获取access_token的接口
url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"

# 从环境变量获取应用凭证
app_id = os.getenv("LARK_APP_ID")
app_secret = os.getenv("LARK_APP_SECRET")

if not app_id or not app_secret:
    print("错误: 未在环境变量或 .env 文件中找到 LARK_APP_ID 或 LARK_APP_SECRET")
    exit(1)

headers = {
    "Content-Type": "application/json"
}

data = {
    "app_id": app_id,
    "app_secret": app_secret
}

try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    
    if result.get("code") == 0:
        access_token = result.get("app_access_token")
        print("成功获取access_token！")
        print("-" * 60)
        print(f"access_token: {access_token}")
        print("-" * 60)
        print("\n请将此access_token复制到您的脚本中使用")
    else:
        print(f"获取access_token失败: {result.get('msg')}")
        print(f"错误码: {result.get('code')}")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
except Exception as e:
    print(f"发生错误: {e}")
