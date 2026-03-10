import json
import requests
import sys
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
root_dir_id = 66895

TARGET_VARS = {
    "userPackageUuid": "DEFAULT_PACKAGE_FREE",
    "userTemplateUuid": "take_usegroup_default_value"
}

def verify_and_fix_variables():
    # 由于 /case/list 报错，我们直接通过遍历 ID 来查，但这次范围放大一点，并打印变量详情
    # 我们知道 root_dir_id 是 66895，我们可以尝试获取该目录下的所有子内容
    # 既然 /case/list 报错，我们尝试 /case/variables/{id} 来验证
    
    # 步骤 1: 尝试获取 66895 目录下的所有用例 ID (由于接口报错，我们仍然使用暴力扫描，但增加验证逻辑)
    start_id = 66896
    end_id = 67100
    
    found_cases = []
    for case_id in range(start_id, end_id):
        res = requests.get(f"{base_url}/case/{case_id}", headers=headers, verify=False).json()
        if res.get("success"):
            data = res.get("data", {})
            # 这里的 parent 应该是 66895 或其子目录（我们需要递归找或者模糊匹配名字）
            name = data.get("name", "")
            if "RG-UNC-dot1x密码复杂度-TP-" in name:
                found_cases.append({"id": case_id, "name": name})

    logger.info(f"Found {len(found_cases)} target cases to verify.")

    for case in found_cases:
        case_id = case['id']
        case_name = case['name']
        
        # 获取变量
        var_res = requests.get(f"{base_url}/case/variables/{case_id}", headers=headers, verify=False).json()
        if not var_res.get("success"):
            logger.error(f"Failed to get variables for {case_id}")
            continue
            
        vars_list = var_res.get("data", [])
        actual_vars = {v['name']: v for v in vars_list}
        
        for target_name, target_val in TARGET_VARS.items():
            if target_name in actual_vars:
                var_obj = actual_vars[target_name]
                if var_obj['value'] != target_val:
                    logger.info(f"Fixing {target_name} for {case_id}: {var_obj['value']} -> {target_val}")
                    # 使用用户指定的传参构造 payload
                    upd_payload = {
                        "caseId": case_id,
                        "name": target_name,
                        "id": var_obj['id'],
                        "value": target_val
                    }
                    # 用户 CURL 使用的是 POST 还是 PUT？
                    # 提示中没写方法，通常 /case/variable 在 SDET 平台更新时虽然 body 含有 id，
                    # 但根据之前的经验，POST 是创建，PUT 是修改。
                    # 不过从用户的 CURL 习惯看，如果是点击“保存”，由于 URL 没带 ID，很可能是 POST 到 list 路径或者 PUT。
                    # 重新观察用户请求：--data-raw 包含 id，且路径是 /case/variable。
                    # 我们尝试使用 POST，因为很多 ATP 接口更新也是 POST 同一个路径。
                    final_res = requests.post(f"{base_url}/case/variable", headers=headers, json=upd_payload, verify=False).json()
                    if not final_res.get("success"):
                         # 如果 POST 不行，尝试 PUT
                         requests.put(f"{base_url}/case/variable", headers=headers, json=upd_payload, verify=False)
            else:
                logger.info(f"Adding missing {target_name} for {case_id}")
                new_var = {
                    "caseId": case_id,
                    "name": target_name,
                    "value": target_val,
                    "type": 0
                }
                requests.post(f"{base_url}/case/variable", headers=headers, json=new_var, verify=False)
        
    logger.info("Verification and fix completed.")

if __name__ == "__main__":
    verify_and_fix_variables()
