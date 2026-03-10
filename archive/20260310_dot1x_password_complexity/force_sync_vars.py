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

def force_update_all():
    # 暴力扫描所有 ID
    start_id = 66920
    end_id = 67050
    
    for cid in range(start_id, end_id):
        # 1. Get current vars to find IDs
        var_res = requests.get(f"{base_url}/case/variables/{cid}", headers=headers, verify=False).json()
        if not var_res.get("success"):
            continue
            
        vars_list = var_res.get("data", [])
        actual_vars = {v['name']: v for v in vars_list}
        
        updated = False
        for target_name, target_val in TARGET_VARS.items():
            if target_name in actual_vars:
                var_obj = actual_vars[target_name]
                # 无论当前值是什么，都强制发一次 POST 刷新
                payload = {
                    "caseId": cid,
                    "name": target_name,
                    "id": var_obj['id'],
                    "value": target_val
                }
                res = requests.post(f"{base_url}/case/variable", headers=headers, json=payload, verify=False).json()
                if res.get("success"):
                    updated = True
        
        if updated:
            logger.info(f"Forced sync for Case {cid}")

if __name__ == "__main__":
    force_update_all()
