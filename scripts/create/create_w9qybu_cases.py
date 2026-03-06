#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
在自动化平台 66588 目录下创建 W9QybU (认证VLAN授权优化) 的自动化用例
1. 创建子目录（认证触发-VLAN下发 / 站点管理 / 授权优先级）
2. 创建 8 条自动化用例
3. 为每条用例添加公共步骤引用 (51401)
4. 将用例ID回写到飞书表格 M 列（脚本序号）
"""

import sys
import os
import json
import time
import requests
import urllib3

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))

# ── 平台配置 ──
BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
TOKEN = "NDY7d2VpYmluOzE3NzQyMzUwMDczOTY7MTcyZTFiNDQyYWVlZjkwM2FkNTU2ZDdhZTMwODhiYzJkNmEzYjAyNmUyMmZiMTJjNjExNmIwNWQwZGIxOWM3MA=="
CREATOR_NAME = "魏斌"
CREATOR_ID = "46"
HEADERS = {"token": TOKEN, "Content-Type": "application/json"}

PARENT_DIR_ID = 66588  # 目标父目录

# ── 飞书配置 ──
APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "W9QybU"
LARK_BASE = "https://open.feishu.cn/open-apis"

WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')


# ══════════════════════════════════════════════════════
# 平台 API
# ══════════════════════════════════════════════════════

def api_post(endpoint, payload):
    resp = requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, json=payload, verify=False, timeout=30)
    return resp.json() if resp.status_code == 200 else {"success": False, "resMessage": f"HTTP {resp.status_code}"}


def create_directory(name, parent_id):
    payload = {
        "name": name,
        "caseType": 0,
        "parent": parent_id,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID,
        "status": 0,
        "deleted": 0,
    }
    rv = api_post("/case", payload)
    if rv.get("success"):
        return rv["data"]
    print(f"    [ERROR] 创建目录失败: {rv.get('resMessage')}")
    return None


def create_case(name, description, parent_id, priority=2):
    payload = {
        "productId": 1,
        "componentId": "1",
        "name": name,
        "priority": priority,
        "note": description,
        "caseType": 1,
        "type": 1,
        "parent": parent_id,
        "creator": CREATOR_NAME,
        "creatorId": CREATOR_ID,
        "modifier": CREATOR_NAME,
        "modifierId": CREATOR_ID,
        "status": 0,
        "deleted": 0,
    }
    rv = api_post("/case", payload)
    if rv.get("success"):
        return rv["data"]
    print(f"    [ERROR] 创建用例失败: {rv.get('resMessage')}")
    return None


def add_public_step(case_id, quote_id="51401"):
    payload = {
        "caseId": case_id,
        "type": "1",
        "status": 0,
        "exception": 0,
        "delayTime": 0,
        "quoteId": quote_id,
    }
    rv = api_post("/flow", payload)
    return rv.get("success", False)


# ══════════════════════════════════════════════════════
# 飞书回写
# ══════════════════════════════════════════════════════

def get_lark_token():
    from lark_sheet_reader import LarkSheetReader
    return LarkSheetReader(APP_ID, APP_SECRET).get_access_token()


def put_lark_range(access_token, range_str, values):
    url = LARK_BASE + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values'
    hdrs = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    resp = requests.put(url, headers=hdrs, json={'valueRange': {'range': range_str, 'values': values}})
    return resp.json()


# ══════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════

def main():
    # 读取分析结果
    result_file = os.path.join(WORKSPACE, 'w9qybu_analysis_result.json')
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    print(f"📂 载入 {len(results)} 条分析结果\n")

    # ── 提取子目录结构 ──
    # 目录分类示例: "VLAN授权优化/认证触发-VLAN下发"
    dir_to_cases = {}
    for r in results:
        cat = r['目录分类']
        sub = cat.split('/')[-1] if '/' in cat else cat
        dir_to_cases.setdefault(sub, []).append(r)

    print(f"子目录结构:")
    for d, cs in dir_to_cases.items():
        print(f"  {d}: {len(cs)} 条用例")
    print()

    # ── Step 1: 创建子目录 ──
    print("=" * 60)
    print("[Step 1] 在 66588 下创建子目录")
    print("=" * 60)
    dir_ids = {}
    for sub_name in dir_to_cases:
        print(f"  创建: {sub_name}")
        did = create_directory(sub_name, PARENT_DIR_ID)
        if did:
            dir_ids[sub_name] = did
            print(f"    [OK] ID: {did}")
        else:
            print(f"    [FAIL]")
        time.sleep(0.3)

    # ── Step 2: 创建用例 + 添加公共步骤 ──
    print(f"\n{'=' * 60}")
    print("[Step 2] 创建自动化用例 + 添加公共步骤引用51401")
    print("=" * 60)
    created = []
    for sub_name, cases in dir_to_cases.items():
        parent_id = dir_ids.get(sub_name)
        if not parent_id:
            print(f"\n  [SKIP] 目录 {sub_name} 创建失败，跳过")
            continue

        print(f"\n  📁 {sub_name} (目录ID: {parent_id})")
        for r in cases:
            cid = r['用例编号']
            case_name = f"{cid}-{r['用例名称']}"
            desc = (
                f"手工用例编号: {cid}\n\n"
                f"用例描述: {r['用例描述']}\n\n"
                f"自动化关键步骤:\n{r['自动化关键步骤']}"
            )
            print(f"    创建: {case_name[:60]}")
            case_id = create_case(case_name, desc, parent_id)
            if case_id:
                print(f"      [OK] 用例ID: {case_id}")
                # 添加公共步骤
                ok = add_public_step(case_id)
                if ok:
                    print(f"      [OK] 已添加公共步骤引用51401")
                else:
                    print(f"      [WARN] 添加公共步骤失败")

                created.append({
                    '用例编号': cid,
                    '用例名称': r['用例名称'],
                    '脚本名称': r['脚本名称'],
                    '平台用例ID': case_id,
                    '目录ID': parent_id,
                    '目录名': sub_name,
                })
            else:
                print(f"      [FAIL]")
            time.sleep(0.3)

    # ── Step 3: 回写飞书 ──
    print(f"\n{'=' * 60}")
    print("[Step 3] 回写用例ID到飞书 M 列（脚本序号）")
    print("=" * 60)
    if created:
        lark_token = get_lark_token()
        # 写表头
        rv = put_lark_range(lark_token, f"{SHEET_ID}!M1:M1", [['脚本序号']])
        print(f"  写表头: code={rv.get('code')}")

        # 构建编号→行号映射（用例从第2行开始）
        cid_to_row = {}
        for i, r in enumerate(results, start=2):
            cid_to_row[r['用例编号']] = i

        for c in created:
            row = cid_to_row.get(c['用例编号'])
            if row:
                rv = put_lark_range(lark_token, f"{SHEET_ID}!M{row}:M{row}", [[c['平台用例ID']]])
                print(f"  {c['用例编号']} → M{row} = {c['平台用例ID']}  code={rv.get('code')}")
                time.sleep(0.3)

    # ── 总结 ──
    print(f"\n{'=' * 60}")
    print("创建完成")
    print("=" * 60)
    print(f"  目录: {len(dir_ids)} 个")
    print(f"  用例: {len(created)} 个")

    for c in created:
        print(f"  {c['用例编号']} | ID={c['平台用例ID']} | {c['用例名称'][:40]}")

    # 保存结果
    out = os.path.join(WORKSPACE, f"w9qybu_creation_result_{int(time.time())}.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({
            'parent_directory': PARENT_DIR_ID,
            'directories': dir_ids,
            'cases': created,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {out}")


if __name__ == "__main__":
    main()
