import json
import requests
import os
import sys
import time
import logging
import urllib3

sys.path.append(r"d:\Code\caseHelper")
from config import Config

urllib3.disable_warnings()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

headers = {
    "token": Config.TEST_PLATFORM_TOKEN,
    "content-type": "application/json"
}

base_url = Config.TEST_PLATFORM_URL
root_dir_id = 66895  # 密码复杂度配置 根目录

# 状态机与公共配置用例 ID 映射
CONFIG_MACRO_MAP = {
    "首次登录强制开+强度检测强制开+定时强制开": 66888,
    "强度检测强制开+定时强制开": 66889,
    "仅开启首次登录强制修改密码": 66890, # 预留
    "关闭所有密码强制校验控制": 66891
}

def get_or_create_directory(name, parent_id):
    """获取或记录目录下子目录 ID，不存在则创建"""
    # 先查询列表
    res = requests.get(f"{base_url}/case/list", params={"parent": parent_id, "caseType": 0}, headers=headers, verify=False).json()
    if res.get("success"):
        for d in res.get("data", []):
            if d['name'] == name:
                return d['id']
    
    # 不存在则创建
    payload = {
        "name": name,
        "parentId": parent_id,
        "productId": 1
    }
    res = requests.post(f"{base_url}/directory", headers=headers, json=payload, verify=False).json()
    if res.get("success"):
        logger.info(f"Created directory: {name} (ID: {res['data']})")
        return res['data']
    return parent_id

def create_e2e_case(case_data, target_dir_id):
    case_no = case_data['用例编号'] # e.g. RG-UNC-dot1x密码复杂度-TP-017
    script_name = case_data.get('脚本名称', '')
    title = f"【{case_no}】{script_name}"
    
    # 1. 确定配置引用 ID
    config_quote_id = 66891
    for key, val in CONFIG_MACRO_MAP.items():
        if key in script_name:
            config_quote_id = val
            break
            
    # 2. 逻辑属性
    auth_success = "断言认证成功" in script_name
    # 提取提取序号 e.g. 017
    seq = case_no.split("-")[-1].replace("TP-", "").replace("TP", "")
    username = f"dot1x密码复杂度{seq}"
    password = "12345aA!" 
    
    # 3. 创建用例
    payload = {
        "name": title,
        "parent": target_dir_id,
        "product": "SAM+",
        "productId": 1,
        "priority": 2,
        "caseType": 1, 
        "isResp": False,
        "componentId": 3, 
        "component": "SAM+v5",
        "description": case_data.get('用例描述', '')
    }
    
    res = requests.post(f"{base_url}/case", headers=headers, json=payload, verify=False).json()
    if not res.get("success"):
        logger.error(f"Failed to create case {title}: {res}")
        return
    
    case_id = res['data']
    logger.info(f"Created Case: {case_id} - {title}")
    
    # 4. 注入变量 (注意加上 type: 0 表示用例变量)
    vars_payload = [
        {"name": "userId2test", "value": username, "note": "开户用户名"},
        {"name": "password2test", "value": password, "note": "开户密码"},
        {"name": "userPackageUuid", "value": "2cf33b8a-3642-4f7f-ac9a-ed80ef4fe563", "note": ""},
        {"name": "userTemplateUuid", "value": "c1f7ced3-a447-4cf0-84cf-ee0c3e72173f", "note": ""},
        {"name": "eap_username", "value": username, "note": "认证用户名"},
        {"name": "eap_password", "value": password, "note": "认证密码"},
        {"name": "userIP", "value": "200.22.1.2", "note": ""},
        {"name": "nasIP", "value": "172.17.9.80", "note": ""},
        {"name": "userMac", "value": "525400541921", "note": ""}
    ]
    
    # 判定失败原因变量
    if "需修改密码" in script_name:
        vars_payload.append({"name": "loginFailMsg", "value": "用户首次登录需修改密码", "note": ""})
    elif "未通过密码强度检测" in script_name:
        vars_payload.append({"name": "loginFailMsg", "value": "未通过密码强度检测", "note": ""})
    elif "密码已过期" in script_name:
        vars_payload.append({"name": "loginFailMsg", "value": "密码已过期", "note": ""})

    for v in vars_payload:
        v["caseId"] = case_id
        v["type"] = 0 # Case Variable
        requests.post(f"{base_url}/case/variable", headers=headers, json=v, verify=False)
        
    # 5. 构建步骤 (type: 1 为引用)
    steps = [
        {"quoteId": 51401, "name": "【公共】管理员密码登录"},
        {"quoteId": config_quote_id, "name": "配置状态机策略"},
        {"quoteId": 51403, "name": "【公共】【开户】指定用户名和密码开户"}
    ]
    
    if auth_success:
        steps.append({"quoteId": 51560, "name": "【公共】【认证】有线1X EAP-MD5 (认证成功)"})
    else:
        steps.append({"quoteId": 66904, "name": "【公共】【认证】有线1X EAP-MD5认证失败"})
        steps.append({"quoteId": 66887, "name": "【公共】查询认证失败原因"})
        
    steps.append({"quoteId": 66891, "name": "【公共配置】恢复密码管控默认配置（全关）"})
    
    for i, step in enumerate(steps):
        flow_payload = {
            "caseId": case_id,
            "order": i + 1,
            "type": 1, # 重要：引用类型
            "quoteId": step["quoteId"],
            "name": step.get("name")
        }
        requests.post(f"{base_url}/flow", headers=headers, json=flow_payload, verify=False)
            
    logger.info(f"Steps added for {case_id}")
    time.sleep(0.5)

def main():
    with open(r'd:\Code\caseHelper\sandbox\workspace\dot1x_passwd_analysis_result.json', 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    auto_cases = [c for c in cases if c.get('是否可自动化') == '是']
    logger.info(f"Total automated cases to process: {len(auto_cases)}")
    
    for case_data in auto_cases:
        # 按“目录分类”创建子目录 e.g. "dot1x密码复杂度/认证组合-首次登录"
        category_path = case_data.get('目录分类', '未分类')
        # 提取最后一级作为子目录名
        sub_dir_name = category_path.split('/')[-1]
        target_dir_id = get_or_create_directory(sub_dir_name, root_dir_id)
        
        create_e2e_case(case_data, target_dir_id)

if __name__ == "__main__":
    main()
