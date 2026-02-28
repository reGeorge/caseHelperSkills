#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断认证问题
"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PLATFORM_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ=="

print("=" * 80)
print("认证诊断")
print("=" * 80)
print(f"平台地址: {PLATFORM_URL}")
print(f"Token: {TOKEN}")
print("-" * 80)

# 测试1: 使用 token header
print("\n测试1: 使用 'token' header")
url = f"{PLATFORM_URL}/case/66241"
headers = {
    "token": TOKEN,
    "Content-Type": "application/json"
}
print(f"请求: GET {url}")
print(f"Headers: {headers}")
resp = requests.get(url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:200]}")

# 测试2: 使用 Authorization Bearer header
print("\n测试2: 使用 'Authorization: Bearer' header")
url = f"{PLATFORM_URL}/case/66241"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
print(f"请求: GET {url}")
print(f"Headers: {headers}")
resp = requests.get(url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:200]}")

# 测试3: 使用 Authorization header (不带 Bearer)
print("\n测试3: 使用 'Authorization' header (不带 Bearer)")
url = f"{PLATFORM_URL}/case/66241"
headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}
print(f"请求: GET {url}")
print(f"Headers: {headers}")
resp = requests.get(url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:200]}")

# 测试4: 解码 Base64 Token
print("\n测试4: Token 解码测试")
try:
    import base64
    decoded = base64.b64decode(TOKEN)
    print(f"解码结果: {decoded}")
except Exception as e:
    print(f"解码失败: {e}")

# 测试5: 测试列表接口
print("\n测试5: 测试列表接口")
url = f"{PLATFORM_URL}/case/list"
headers = {
    "token": TOKEN,
    "Content-Type": "application/json"
}
params = {"caseType": 0}
print(f"请求: GET {url}")
print(f"Params: {params}")
resp = requests.get(url, headers=headers, params=params, verify=False)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:500]}")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)
print("\n如果所有测试都返回 401，可能的原因：")
print("1. Token 已过期")
print("2. Token 格式不正确")
print("3. 平台需要用户登录后才能获取 Token")
print("4. Token 需要从平台界面重新生成")
print("\n建议联系平台管理员获取有效的 Token")
