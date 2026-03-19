#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AD LDAPs 自动化用例 ID 回写 + Portal 用例 status=1 设置

任务：
  1. 将自动化用例 ID 回写到飞书表格 9dhc17 的 G 列（新增"自动化用例ID"列）
  2. 将 12 条 Portal 打流用例的 status 设置为 1（已通过）

飞书表格：https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=9dhc17
平台 Token：环境变量 TEST_PLATFORM_TOKEN
"""
import sys
import os
import json
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'lark-skills', 'lark-sheet-writer'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'sdet-skills', 'platform-client'))

from lark_sheet_writer import LarkSheetWriter
from platform_client import PlatformClient

# ── 凭证 / 参数 ────────────────────────────────────────────────
APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "9dhc17"

PLATFORM_TOKEN = os.environ.get("TEST_PLATFORM_TOKEN", "")
if not PLATFORM_TOKEN:
    print("❌ 未设置 TEST_PLATFORM_TOKEN 环境变量")
    sys.exit(1)

# ── 读取 Phase 2 结果 ──────────────────────────────────────────
result_path = os.path.join(PROJECT_ROOT, 'sandbox', 'workspace', 'ad_ldaps_phase2_result.json')
with open(result_path, encoding='utf-8') as f:
    phase2 = json.load(f)

cases = phase2['cases']  # 12 个状态，每个含 setup/portal/gtc/mschapv2/ttlspap

# ── 构建 手工用例行 → 自动化用例ID 映射 ──────────────────────
# 9dhc17 手工用例行号（1-based）与自动化用例ID 的对应关系
# 行号说明：行1=表头，行2=001，行3=002，...，行40=039
#
# 手工用例 001-003 为配置校验类，无对应打流自动化用例 → 留空
# 手工用例 004-039 按顺序对应 12 个状态 × 3 种打流类型（portal / GTC / MschapV2）
# 注意：原手工用例中无 TTLS-PAP，故该类型自动化用例不写回

# 状态排列顺序（与手工用例编号 004-039 一一对应）：
# 001 单域+关闭SSL:     row5=portal, row6=GTC, row7=MschapV2
# ...
# 012 主备域+私有证书:  row38=portal, row39=GTC, row40=MschapV2

g_column_values = [["自动化用例ID"]]  # G1 表头

# 行2-4：001-003 无匹配，填空
for _ in range(3):
    g_column_values.append([""])

# 行5-40：004-039 按 状态 × 打流类型
for state_data in cases:  # 12 个状态，state=1..12
    portal_id = state_data['portal']
    gtc_id = state_data['gtc']
    mschapv2_id = state_data['mschapv2']
    g_column_values.append([str(portal_id)])    # portal行
    g_column_values.append([str(gtc_id)])       # GTC行
    g_column_values.append([str(mschapv2_id)])  # MschapV2行

total_rows = len(g_column_values)  # 应为 40（G1到G40）
assert total_rows == 40, f"期望 40 行，实际 {total_rows} 行"

print(f"{'='*60}")
print("  任务 1：回写自动化用例 ID 到飞书 9dhc17 G 列")
print(f"{'='*60}")
print(f"准备写入 {total_rows} 行到 {SHEET_ID}!G1:G{total_rows}")

# ── 写入飞书 ──────────────────────────────────────────────────
writer = LarkSheetWriter(APP_ID, APP_SECRET)

range_str = f"{SHEET_ID}!G1:G{total_rows}"
result = writer.update_range(SPREADSHEET_TOKEN, range_str, g_column_values)

if result.get('success'):
    updated = result.get('data', {}).get('updated_rows', '?') if isinstance(result.get('data'), dict) else '?'
    print(f"✅ 飞书回写成功！range={range_str}  updated_rows={updated}")
else:
    print(f"❌ 飞书回写失败: {result}")
    sys.exit(1)

# 打印回写摘要
print("\n回写内容预览（前10行）：")
for i, row in enumerate(g_column_values[:10]):
    print(f"  G{i+1}: {row[0]}")
print(f"  ... (共 {total_rows} 行)")

# ── 任务 2：设置 Portal 用例 status=1 ─────────────────────────
print(f"\n{'='*60}")
print("  任务 2：设置 12 条 Portal 用例 status=1")
print(f"{'='*60}")

BASE_URL = "https://sdet.ruishan.cc/api/sdet-atp"
pc = PlatformClient(base_url=BASE_URL, token=PLATFORM_TOKEN, creator_name="魏斌", creator_id=46)
base_url = pc.base_url

portal_ids = [str(c['portal']) for c in cases]
print(f"Portal 用例 IDs: {portal_ids}\n")

success_count = 0
fail_count = 0
import urllib3
urllib3.disable_warnings()

for case_id in portal_ids:
    # GET 完整用例数据
    get_resp = requests.get(
        f"{base_url}/case/{case_id}",
        headers=pc.headers,
        verify=False
    )
    if get_resp.status_code != 200 or not get_resp.json().get('success'):
        print(f"  ❌ [{case_id}] 获取用例失败: {get_resp.text[:100]}")
        fail_count += 1
        continue

    detail = get_resp.json()['data']
    old_status = detail.get('status', 'N/A')
    detail['status'] = 1
    detail['modifier'] = pc.creator_name
    detail['modifierId'] = pc.creator_id

    # POST 更新
    post_resp = requests.post(
        f"{base_url}/case",
        headers=pc.headers,
        json=detail,
        verify=False
    )
    if post_resp.status_code == 200 and post_resp.json().get('success'):
        print(f"  ✅ [{case_id}] status: {old_status} → 1  ({detail.get('name', '')[:40]})")
        success_count += 1
    else:
        print(f"  ❌ [{case_id}] 更新失败: {post_resp.text[:100]}")
        fail_count += 1

print(f"\n{'='*60}")
print(f"  Portal status 更新汇总: ✅ {success_count}/12  ❌ {fail_count}/12")
print(f"{'='*60}")

# ── 保存结果日志 ──────────────────────────────────────────────
log = {
    'lark_writeback': {
        'range': range_str,
        'rows': total_rows,
        'success': result.get('success'),
    },
    'portal_status_update': {
        'portal_ids': portal_ids,
        'success_count': success_count,
        'fail_count': fail_count,
    },
    'case_mapping': [
        {
            'lark_row': 5 + i * 3,
            'manual_no': f'AD对接支持LDAPs-{4 + i * 3:03d}',
            'portal_id': cases[i]['portal'],
            'gtc_id': cases[i]['gtc'],
            'mschapv2_id': cases[i]['mschapv2'],
        }
        for i in range(12)
    ]
}
log_path = os.path.join(PROJECT_ROOT, 'sandbox', 'workspace', 'ad_ldaps_writeback_log.json')
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
print(f"\n日志已保存: {log_path}")
