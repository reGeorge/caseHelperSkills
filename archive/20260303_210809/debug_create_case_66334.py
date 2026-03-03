#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为用例66334创建步骤和变量
场景：接入方式未勾选MAC快速接入，无感接入类型为仅有线，用户进行有线认证
预期：不生成无感记录
"""

import sys
import os
import requests
import urllib3

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 添加skill路径
skill_path = os.path.join(project_root, 'skills', 'sdet-skills', 'sdet-api-helper')
sys.path.insert(0, skill_path)

try:
    from sdet_api_info import _client
except ImportError:
    # 如果导入失败，直接使用requests
    print("无法导入sdet_api_info，使用直接的API调用")
    _client = None

# 配置
BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="
CREATOR_NAME = "魏斌"
CREATOR_ID = 46

# 通用headers
HEADERS = {
    "token": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*"
}


def create_variable(case_id, var_name, var_value):
    """创建变量"""
    url = f"{BASE_URL}/case/variable"
    payload = {
        "caseId": case_id,
        "name": var_name,
        "value": var_value
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                print(f"  [OK] 变量创建成功: {var_name} = {var_value}")
                return True
            else:
                print(f"  [FAIL] 变量创建失败: {var_name} - {res_json.get('resMessage')}")
        else:
            print(f"  [ERROR] 变量创建HTTP错误: {var_name} - 状态码={resp.status_code}")
    except Exception as e:
        print(f"  [EXCEPTION] 变量创建异常: {var_name} - {e}")
    
    return False


def create_flow(case_id, flow_data):
    """创建步骤"""
    url = f"{BASE_URL}/flow"
    
    # 基础字段
    payload = {
        "caseId": case_id,
        "status": 0,
        "deleted": 0,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID
    }
    
    # 根据类型构造不同的payload
    if flow_data.get("type") == 1:
        # 公共步骤引用
        payload.update({
            "type": "1",
            "quoteId": flow_data.get("quoteId"),
            "name": flow_data.get("name", ""),
            "exception": flow_data.get("exception", 0),
            "delayTime": flow_data.get("delayTime", 0)
        })
    else:
        # 普通HTTP请求步骤
        payload.update({
            "type": 0,
            "name": flow_data.get("name", ""),
            "order": flow_data.get("order", 1),
            "host": flow_data.get("host", "${G_host}"),
            "port": flow_data.get("port"),
            "protocol": flow_data.get("protocol", 0),
            "path": flow_data.get("path", ""),
            "method": flow_data.get("method", "POST"),
            "headers": flow_data.get("headers", []),
            "body": flow_data.get("body", "{}"),
            "params": flow_data.get("params", []),
            "variables": flow_data.get("variables", []),
            "check": flow_data.get("check", []),
            "exception": flow_data.get("exception", 1),
            "responseTime": 0,
            "note": flow_data.get("note", ""),
            "cookieClean": flow_data.get("cookieClean", 0),
            "delayTime": flow_data.get("delayTime", 0),
            "ipVersion": flow_data.get("ipVersion", 0)
        })
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("success"):
                flow_id = res_json.get("data")
                print(f"  [OK] 步骤创建成功，ID: {flow_id}")
                return flow_id
            else:
                print(f"  [FAIL] 步骤创建失败: {res_json.get('resMessage')}")
        else:
            print(f"  [ERROR] 步骤创建HTTP错误: 状态码={resp.status_code}")
    except Exception as e:
        print(f"  [EXCEPTION] 步骤创建异常: {e}")
    
    return None


def create_variables_for_case_66334(case_id):
    """创建用例变量（复用65633的变量）"""
    variables = [
        {"name": "userIP", "value": "5.1.1.2"},
        {"name": "nasIP", "value": "172.17.9.80"},
        {"name": "userMac", "value": "525400541900"},
        {"name": "Portal_username", "value": "autotestyx001"},
        {"name": "Portal_password", "value": "Shyfzx@163"},
        {"name": "userssid", "value": "rcc"},
        {"name": "cepevlan", "value": "3"},
        {"name": "domain", "value": "default"},
        {"name": "userId2test", "value": "autotestyx001"}
    ]
    
    print(f"\n{'='*60}")
    print(f"开始为用例 {case_id} 创建 {len(variables)} 个变量")
    print(f"{'='*60}")
    
    created_count = 0
    for var in variables:
        if create_variable(case_id, var["name"], var["value"]):
            created_count += 1
    
    print(f"\n变量创建完成: {created_count}/{len(variables)}")
    return created_count


def create_steps_for_case_66334(case_id):
    """创建用例步骤"""
    steps = [
        # 步骤1: 管理员登录
        {
            "type": 1,
            "quoteId": "55635",
            "name": "【公共】【鉴权】UNC管理端登录（admin账号）",
            "exception": 0,
            "delayTime": 0,
            "order": 1
        },
        # 步骤2: 清理环境
        {
            "type": 1,
            "quoteId": "65758",
            "name": "【公共】 删除无感认证-指定用户名",
            "exception": 0,
            "delayTime": 0,
            "order": 2
        },
        # 步骤3: 有线认证
        {
            "type": 1,
            "quoteId": "65650",
            "name": "【UNC公共】有线二代web认证全流程",
            "exception": 0,
            "delayTime": 0,
            "order": 3
        },
        # 步骤4: 查看绑定信息（不校验字段）
        {
            "type": 0,
            "name": "查看绑定信息",
            "order": 4,
            "host": "${G_samhost}",
            "port": "${G_samport}",
            "protocol": 0,
            "path": "/sam/api/admin/networkBindInfo/query",
            "method": 1,
            "headers": [
                {
                    "id": "bind01",
                    "key": "Content-Type",
                    "value": "application/json;charset=utf-8"
                }
            ],
            "body": '{"pageIndex":1,"pageSize":10,"sort":[],"userId":"${Portal_username}"}',
            "params": [],
            "variables": [],
            "check": [],
            "exception": 1,
            "responseTime": 0,
            "note": "查询绑定信息，不校验字段",
            "cookieClean": 0,
            "delayTime": 0,
            "ipVersion": 0
        },
        # 步骤5: 查看无感记录（预期不生成记录）
        {
            "type": 0,
            "name": "查看无感记录",
            "order": 5,
            "host": "${G_samhost}",
            "port": "${G_samport}",
            "protocol": 1,
            "path": "/sam/api/admin/userMab/list",
            "method": 1,
            "headers": [
                {
                    "id": "mab01",
                    "key": "Content-Type",
                    "value": "application/json;charset=utf-8"
                }
            ],
            "body": '{"pageIndex":1,"pageSize":10,"sort":[],"userId":"${Portal_username}"}',
            "params": [],
            "variables": [],
            "check": [
                {
                    "id": "check01",
                    "expression": "$.data.total",
                    "expectValue": "0",
                    "assertContent": 10,
                    "operator": 0
                }
            ],
            "exception": 1,
            "responseTime": 0,
            "note": "预期不生成无感记录，验证total=0",
            "cookieClean": 0,
            "delayTime": 0,
            "ipVersion": 0
        }
    ]
    
    print(f"\n{'='*60}")
    print(f"开始为用例 {case_id} 创建 {len(steps)} 个步骤")
    print(f"{'='*60}")
    
    created_count = 0
    for idx, step in enumerate(steps, 1):
        step_type = "公共步骤引用" if step.get("type") == 1 else "HTTP请求步骤"
        print(f"\n[步骤{idx}] {step['name']} ({step_type})")
        
        if create_flow(case_id, step):
            created_count += 1
    
    print(f"\n步骤创建完成: {created_count}/{len(steps)}")
    return created_count


def main():
    """主函数：为用例66334创建步骤和变量"""
    case_id = 66334
    
    print(f"\n{'#'*60}")
    print(f"# 开始为用例 {case_id} 创建自动化内容")
    print(f"# 场景：接入方式未勾选MAC快速接入，无感接入类型为仅有线")
    print(f"# 预期：不生成无感记录")
    print(f"{'#'*60}")
    
    # 1. 创建变量
    var_count = create_variables_for_case_66334(case_id)
    
    # 2. 创建步骤
    step_count = create_steps_for_case_66334(case_id)
    
    # 3. 汇总
    print(f"\n{'='*60}")
    print(f"创建完成汇总")
    print(f"{'='*60}")
    print(f"变量: {var_count}/9")
    print(f"步骤: {step_count}/5")
    
    if var_count == 9 and step_count == 5:
        print(f"\n[SUCCESS] 全部创建成功！")
        print(f"\n建议下一步操作:")
        print(f"1. 访问平台查看用例: https://sdet.ruishan.cc/ap/atp/apiCase/detail/{case_id}")
        print(f"2. 触发用例调试验证")
    else:
        print(f"\n[WARNING] 部分创建失败，请检查日志")


if __name__ == "__main__":
    main()
