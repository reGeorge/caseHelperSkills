#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
目录批量同步与精简签名生成脚本
用途：从SDET平台指定父目录 (如 51399) 递归拉取所有“公共用例”，
并将它们萃取为极简的 JSON 对象 (仅包含 Inputs 和 Outputs)，用于 AI 组装。
自动注册好记的别名至 knowledge/common_cases_manifest.json。
"""

import os
import sys
import json
import logging
import requests
import re

# 确保脚本能在任意层级执行并引用到依赖
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(base_path)

from config import Config
import importlib.util

# 动态加载 PlatformClient
platform_client_path = os.path.join(base_path, 'skills', 'sdet-skills', 'platform-client', 'platform_client.py')
spec = importlib.util.spec_from_file_location("platform_client", platform_client_path)
pc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc_module)
PlatformClient = pc_module.PlatformClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DirectoryCaseSync:
    def __init__(self, root_dir_id):
        self.root_dir_id = root_dir_id
        self.client = PlatformClient(
            base_url=Config.TEST_PLATFORM_URL,
            token=Config.TEST_PLATFORM_TOKEN
        )
        self.manifest_path = Config.MANIFEST_PATH
        self.cases_dir = Config.COMMON_CASES_DIR
        
        # 建立别名注册表
        self.manifest = self.load_manifest()

    def load_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def save_manifest(self):
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=4)
            
    def generate_alias(self, name, case_id):
        """
        根据中文名称生成一个用于大模型理解的合法别名。
        由于我们可能没有现成的汉字转拼音库，简单采用关键词提取或直接给全拼、id组合。
        在这里利用一个纯净的映射规则：过滤特殊符号。
        """
        # 移除符号
        clean_name = re.sub(r'[^\w\s]', '_', name)
        clean_name = clean_name.replace(' ', '')
        
        # 如果已经有了相同 case_id 的别名，优先继承
        for k, v in self.manifest.items():
            if v == case_id:
                return k
                
        # 否则生成名为 common_xxx_ID 的英文别名备选，或者直接用清理后的名称
        # 为防止全中文别名引发兼容性问题，我们将用例id作为兜底后缀
        alias = f"case_{case_id}"
        
        # 尝试匹配已知动作以改善别名
        if "登录" in name:
            alias = f"login_{case_id}"
        elif "开户" in name:
            alias = f"register_{case_id}"
        elif "清理" in name or "删除" in name:
            alias = f"cleanup_{case_id}"
            
        return alias
        
    def traverse_directory(self, dir_id):
        """递归遍历目录获取所有的测试用例"""
        logging.info(f"📁 正在遍历目录: {dir_id}")
        resp = self.client.get_cases_children(dir_id)
        if not resp.get("success"):
            logging.error(f"❌ 遍历目录 {dir_id} 失败: {resp.get('message')}")
            return []
            
        children = resp.get("data", [])
        all_cases = []
        
        for item in children:
            if item.get("caseType") == 0:  # 子目录
                sub_cases = self.traverse_directory(item.get("id"))
                all_cases.extend(sub_cases)
            else:  # 用例 (Type=1或2)
                all_cases.append(item)
                
        return all_cases

    def fetch_case_inputs(self, case_id):
        """拉取用例变量作为输入参数"""
        vars_url = f"{self.client.base_url}/case/variables/{case_id}"
        try:
            resp = requests.get(vars_url, headers=self.client.headers, verify=False).json()
            if resp.get("success"):
                return resp.get("data", [])
            return []
        except Exception:
            return []
            
    def fetch_case_outputs(self, case_id):
        """从步骤中拉取提取器作为输出变量"""
        resp = self.client.list_steps(case_id)
        if not resp.get("success"):
            return []
            
        outputs = []
        steps = resp.get("data", [])
        for step in steps:
            # 兼容：有时候叫 variables，有时候藏在提取器里
            extractors = step.get("variables", [])
            if extractors:
                for ext in extractors:
                    if ext.get("name"):
                        # 去重
                        if not any(o.get("name") == ext.get("name") for o in outputs):
                            outputs.append({
                                "name": ext.get("name"),
                                "expression": ext.get("expression")
                            })
        return outputs

    def sync(self):
        if not os.path.exists(self.cases_dir):
            os.makedirs(self.cases_dir)
            
        logging.info(f"🚀 开始全量同步目录 {self.root_dir_id} 下的用例，转化为函数签名...")
        cases = self.traverse_directory(self.root_dir_id)
        logging.info(f"✅ 共发现 {len(cases)} 个子用例，开始分析提取...")
        
        for case in cases:
            case_id = case.get("id")
            name = case.get("name")
            desc = case.get("description", "")
            
            # 生成别名
            alias = self.generate_alias(name, case_id)
            self.manifest[alias] = case_id
            
            logging.info(f"🔄 正在处理用例: {name} ({alias})")
            
            # 解析 Inputs & Outputs
            raw_vars = self.fetch_case_inputs(case_id)
            inputs = [{"name": v.get("name"), "value": v.get("value"), "note": v.get("note", "")} for v in raw_vars]
            outputs = self.fetch_case_outputs(case_id)
            
            # 智能推断或兜底伪描述
            if not desc:
                # 伪造一段适合组装和AI理解的描述
                desc = (
                    f"功能说明：该公共步骤主要用于 '{name}' 操作。\n"
                    f"依赖入参：{', '.join([i['name'] for i in inputs]) if inputs else '无依赖'}\n"
                    f"抛出变量：{', '.join([o['name'] for o in outputs]) if outputs else '无抛出'}"
                )
                
            # 拼装精简版的签名结构
            signature_data = {
                "alias": alias,
                "case_id": case_id,
                "name": name,
                "description": desc,
                "inputs": inputs,       # 提供给下游修改的变量列表
                "outputs": outputs      # 完成后暴露给后续用例的提取器变量
            }
            
            output_file = os.path.join(self.cases_dir, f"{alias}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(signature_data, f, ensure_ascii=False, indent=2)
                
        # 写回manifest
        self.save_manifest()
        logging.info("🎉 批量学习与同步完成！新的函数签名已入库。")

if __name__ == "__main__":
    sync_job = DirectoryCaseSync(51399)
    sync_job.sync()
