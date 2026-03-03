import requests
import json

# Token配置
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="

headers = {
    'token': TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# 1. 获取用例详情
print("=" * 60)
print("1. 获取用例详情 (case_id: 65633)")
print("=" * 60)
case_url = "https://sdet.ruishan.cc/api/sdet-atp/case/v2/65633"
resp = requests.get(case_url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    case_detail = resp.json()
    print(f"用例名称: {case_detail.get('name')}")
    print(f"用例描述: {case_detail.get('description')}")
    print(f"所属目录: {case_detail.get('directoryId')}")
    print(f"用例类型: {case_detail.get('type')}")
    print(f"创建者: {case_detail.get('creatorName')}")
    # 保存完整用例信息
    with open('case_65633_detail.json', 'w', encoding='utf-8') as f:
        json.dump(case_detail, f, ensure_ascii=False, indent=2)
    print("\n完整用例信息已保存到 case_65633_detail.json")
else:
    print(f"请求失败: {resp.text}")
    exit(1)

# 2. 获取步骤列表
print("\n" + "=" * 60)
print("2. 获取步骤列表 (case_id: 65633)")
print("=" * 60)
flow_url = "https://sdet.ruishan.cc/api/sdet-atp/flows/65633"
resp = requests.get(flow_url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    flow_data = resp.json()
    flows = flow_data.get('data', [])
    print(f"步骤总数: {len(flows)}")
    for idx, flow in enumerate(flows, 1):
        print(f"\n步骤{idx}: {flow.get('name')}")
        print(f"  - 顺序: {flow.get('order')}")
        print(f"  - 协议: {flow.get('protocol')} (0=HTTP, 1=HTTPS)")
        print(f"  - 方法: {flow.get('method')}")
        print(f"  - 路径: {flow.get('path')}")
        print(f"  - Host: {flow.get('host')}")
        # 保存完整步骤信息
        with open('case_65633_flows.json', 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, ensure_ascii=False, indent=2)
    print("\n完整步骤信息已保存到 case_65633_flows.json")
else:
    print(f"请求失败: {resp.text}")

# 3. 获取变量列表
print("\n" + "=" * 60)
print("3. 获取变量列表 (case_id: 65633)")
print("=" * 60)
var_url = "https://sdet.ruishan.cc/api/sdet-atp/case/variables/65633"
resp = requests.get(var_url, headers=headers, verify=False)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    var_data = resp.json()
    variables = var_data.get('data', [])
    print(f"变量总数: {len(variables)}")
    for idx, var in enumerate(variables, 1):
        print(f"\n变量{idx}: {var.get('name')}")
        print(f"  - 值: {var.get('value')}")
        print(f"  - 描述: {var.get('description')}")
    # 保存完整变量信息
    with open('case_65633_variables.json', 'w', encoding='utf-8') as f:
        json.dump(var_data, f, ensure_ascii=False, indent=2)
    print("\n完整变量信息已保存到 case_65633_variables.json")
else:
    print(f"请求失败: {resp.text}")

print("\n" + "=" * 60)
print("分析完成！")
print("=" * 60)
