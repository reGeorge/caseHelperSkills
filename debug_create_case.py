"""
调试SDET创建用例API返回结果
"""
import requests
import json
import yaml

# 读取配置
with open('agent_service/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

base_url = config['secrets']['SDET_BASE_URL']
token = config['secrets']['SDET_API_TOKEN']

print(f"Base URL: {base_url}")
print(f"Token: {token[:20]}...\n")

# 构造用例数据
payload = {
    "directoryId": 66328,
    "name": "测试用例-有线认证-调试",
    "description": "这是一个调试测试用例",
    "precondition": "预置条件测试",
    "steps": [
        {
            "content": "步骤1: 配置参数",
            "expected": "配置成功"
        },
        {
            "content": "步骤2: 执行测试",
            "expected": "执行成功"
        }
    ],
    "level": 2,
    "tags": ["有线认证", "调试"]
}

print("请求体:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "="*60)

# 发送创建请求
url = f"{base_url}/cases"
headers = {
    "token": token,
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload, verify=False)

print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}\n")
print(f"响应文本:")
print(response.text)

# 解析响应
try:
    result = response.json()
    print("\n" + "="*60)
    print("JSON解析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 检查返回结构
    print("\n" + "="*60)
    print("返回结构分析:")
    print(f"success字段: {result.get('success')}")
    print(f"resCode字段: {result.get('resCode')}")
    print(f"resMessage字段: {result.get('resMessage')}")
    print(f"data字段: {result.get('data')}")
    
    if 'data' in result:
        print(f"data.id: {result['data'].get('id')}")
        print(f"data字段类型: {type(result['data'])}")
        if isinstance(result['data'], dict):
            print(f"data所有字段: {list(result['data'].keys())}")
        
except Exception as e:
    print(f"\nJSON解析失败: {e}")
