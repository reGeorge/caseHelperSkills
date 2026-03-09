#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心知识库同步脚本
用途：从SDET平台全量或部分拉取配置好的“公共步骤/用例”（在知识库的Manifest文件中指定），
并覆盖到本地的 knowledge/common_cases/ 目录下，以便进行版本控制和被AI/代码直接读取利用。
"""

import os
import sys
import json
import logging

# 确保脚本能在任意层级执行并引用到依赖
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(base_path)

# 由于目录名包含连字符 (sdet-skills/platform-client)，我们需要通过动态路径或添加sys.path来导入
platform_client_path = os.path.join(base_path, 'skills', 'sdet-skills', 'platform-client')
sys.path.append(platform_client_path)
from platform_client import PlatformClient
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def sync_knowledge_base():
    if not os.path.exists(config.MANIFEST_PATH):
        logging.error(f"Manifest文件未找到：{config.MANIFEST_PATH}")
        return

    # 1. 挂载和读取配置
    with open(config.MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if not os.path.exists(config.COMMON_CASES_DIR):
        os.makedirs(config.COMMON_CASES_DIR)

    # 2. 初始化平台接口请求客户端
    client = PlatformClient(
        base_url=config.TEST_PLATFORM_URL,
        token=config.TEST_PLATFORM_TOKEN,
        creator_name=config.CREATOR_NAME,
        creator_id=str(config.CREATOR_ID)
    )

    # 3. 遍历并获取平台内容，转写至本地
    for case_alias, case_id in manifest.items():
        logging.info(f"🔄 正在从平台拉取 {case_alias} (用例ID: {case_id})...")
        
        try:
            # ==== 获取用例详情和步骤 ====
            case_resp = client.get_case(case_id)
            if not case_resp.get("success"):
                logging.error(f"❌ 查无此用例或请求失败 (ID:{case_id})")
                continue
                
            case_data = case_resp.get("data", {})
            
            # 同时拉取步骤 (从list_steps接口)
            steps_resp = client.list_steps(case_id)
            steps_data = steps_resp.get("data", []) if steps_resp.get("success") else []
            
            # 方法映射
            method_map = {0: "GET", 1: "POST", 2: "PUT", 3: "DELETE"}
            
            # 简化映射平台步骤
            formatted_steps = []
            for idx, s in enumerate(steps_data):
                step_method_int = s.get("method", 0)
                step_method = method_map.get(step_method_int, str(step_method_int))
                
                fmt_s = {
                    "step_id": s.get("id"),
                    "name": s.get("name", f"第{idx+1}步"),
                    "method": step_method,
                    "path": s.get("path", ""),
                    "headers": { h.get("key", ""): h.get("value", "") for h in s.get("headers", []) if h.get("key") },
                }
                
                # 请求参数与体
                params = s.get("params")
                if params and len(params) > 0:
                    fmt_s["params"] = { p.get("key"): p.get("value") for p in params if p.get("key") }
                
                raw_body = s.get("body")
                if raw_body:
                    try:
                        # 尝试反序列化 JSON Body，如果失败则直接保存字符串
                        fmt_s["body"] = json.loads(raw_body)
                    except:
                        fmt_s["body"] = raw_body

                # 提取器
                vars_ext = s.get("variables")
                if vars_ext and len(vars_ext) > 0:
                    fmt_s["extractors"] = [
                        {"name": v.get("name"), "expression": v.get("expression")}
                        for v in vars_ext
                    ]
                
                # 断言
                checks = s.get("check")
                if checks and len(checks) > 0:
                    fmt_s["assertions"] = [
                        {"expression": c.get("expression"), "expected": c.get("expectValue")}
                        for c in checks
                    ]
                    
                # 运行条件
                conds = s.get("condition")
                if conds and len(conds) > 0:
                    fmt_s["conditions"] = [
                        {"expression": c.get("expression"), "expected": c.get("expectValue")}
                        for c in conds
                    ]

                formatted_steps.append(fmt_s)
                
            # 获取用例变量
            vars_url = f"{client.base_url}/case/variables/{case_id}"
            import requests # 确保引入requests
            vars_resp = requests.get(vars_url, headers=client.headers, verify=False).json()
            case_variables = vars_resp.get("data", []) if vars_resp.get("success") else []
            formatted_case_vars = [{"name": v.get("name"), "value": v.get("value")} for v in case_variables]

            # 组合成本地标准结构
            case_detail = {
                "case_id": case_id,
                "name": case_data.get("name", "未命名公共步骤"),
                "description": case_data.get("description", "由平台同步而来的公共用例"),
                "tags": ["common", case_alias.replace("_steps", "")],
                "case_variables": formatted_case_vars, # 注入这部分
                "steps": formatted_steps
            }

            # 将抓回的字典按特定结构写入 JSON 以被 GIT 控制
            output_file = os.path.join(config.COMMON_CASES_DIR, f"{case_alias}.json")
            with open(output_file, 'w', encoding='utf-8') as fw:
                json.dump(case_detail, fw, ensure_ascii=False, indent=2)
            
            logging.info(f"✅ 拉取成功，已写入: {output_file}")
            
        except Exception as e:
            logging.error(f"❌ 同步 {case_alias} 失败: {str(e)}")

    logging.info("\n🎉 知识库同步完成！如果发生信息覆盖升级，请执行 `git diff knowledge` 查看具体修改。")

if __name__ == "__main__":
    sync_knowledge_base()
