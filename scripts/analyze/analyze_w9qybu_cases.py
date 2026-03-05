#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证VLAN授权优化用例自动化分析脚本
读取飞书表格 W9QybU → 分析自动化可行性 → 生成脚本名称/自动化步骤 → 回写飞书 → 输出报告

现有列: A=测试点描述 B=用例包名称 C=用例标签 D=用例编号 E=用例名称
        F=用例描述 G=预置条件 H=测试步骤 I=期望结果
新增列: J=是否可自动化 K=不可自动化原因 L=脚本名称
"""

import sys
import os
import json
import re
import requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))

from lark_sheet_reader import LarkSheetReader

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "W9QybU"
BASE_URL = "https://open.feishu.cn/open-apis"
REF_LOGIN_ADMIN = "引用51401"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')


# ══════════════════════════════════════════════════════
# 读取飞书表格（处理富文本单元格）
# ══════════════════════════════════════════════════════

def cell_text(cell):
    if cell is None:
        return ''
    if isinstance(cell, str):
        return cell.strip()
    if isinstance(cell, list):
        return ''.join(
            seg['text'] for seg in cell if isinstance(seg, dict) and 'text' in seg
        ).strip()
    return str(cell).strip()


def read_sheet():
    reader = LarkSheetReader(APP_ID, APP_SECRET)
    token = reader.get_access_token()
    hdrs = {'Authorization': 'Bearer ' + token}

    url = BASE_URL + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values/' + SHEET_ID + '!A1:N400'
    raw_rows = requests.get(url, headers=hdrs).json().get('data', {}).get('valueRange', {}).get('values', [])

    col_names = [cell_text(h) for h in raw_rows[0]]
    col_names[0] = '测试点描述'

    cases = []
    for row in raw_rows[1:]:
        if not any(cell_text(c) for c in row):
            continue
        row_dict = {col_names[i]: cell_text(row[i]) if i < len(row) else '' for i in range(len(col_names))}
        if row_dict.get('用例编号', ''):
            cases.append(row_dict)
    return cases


# ══════════════════════════════════════════════════════
# 分类：全部 8 条用例均可 API 自动化
# 认证前置配置（区域/设备纳管/VLAN授权规则）可通过管理端 API 完成
# 认证触发（802.1x/portal/MAB）通过模拟认证接口完成
# 站点管理 CRUD 可通过管理端 API 完成
# ══════════════════════════════════════════════════════

def classify_case(case_id, name, steps, expect):
    return '是', ''


# ══════════════════════════════════════════════════════
# 自动化关键步骤
# ══════════════════════════════════════════════════════

def generate_automation_steps(case_id, name, precondition, steps, expect):
    lines = []
    n = 1

    lines.append(f"{n}. 登录管理端 - {REF_LOGIN_ADMIN}")
    n += 1

    num = case_id.split('-')[-1] if '-' in case_id else ''

    # ── 007: 站点管理 CRUD ──
    if num == '007':
        lines.append(f"{n}. 调用站点管理接口，确认全局模式下可访问「策略-业务授权管理-认证VLAN授权」")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权接口，在站点1下创建授权对象1，在站点2下创建授权对象2，断言创建成功")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权查询接口（站点1），断言仅返回授权对象1")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权查询接口（站点2），断言仅返回授权对象2")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权批量新增接口（站点1），断言新增数据在站点2查询不到")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权批量删除接口（站点1），调用站点2查询接口断言授权对象2不受影响")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用接口删除站点1/2的所有测试授权对象")
        return "\n".join(lines)

    # ── 008: 授权下发优先级 ──
    if num == '008':
        lines.append(f"{n}. 调用认证VLAN授权配置接口，分别创建四类授权规则：")
        n += 1
        lines.append(f"   - 用户MAC(MAC1) → vlan12")
        lines.append(f"   - 用户名(test1) → vlan13")
        lines.append(f"   - 用户组(教学组1) → vlan14")
        lines.append(f"   - 终端类型(PC) → vlan15")
        lines.append(f"{n}. 调用模拟认证接口，使用同时满足四类条件的终端发起认证")
        n += 1
        lines.append(f"{n}. 调用在线用户查询接口或认证响应报文查询接口，断言下发vlanid为12（MAC优先级最高）")
        n += 1
        lines.append(f"{n}. 调用认证VLAN授权配置接口，删除MAC规则，重新触发认证，断言下发vlanid为13")
        n += 1
        lines.append(f"{n}. 删除用户名规则，触发认证，断言下发vlanid为14")
        n += 1
        lines.append(f"{n}. 删除用户组规则，触发认证，断言下发vlanid为15（终端类型最低优先级）")
        n += 1
        lines.append(f"{n}. 断言优先级顺序：用户MAC > 用户名 > 用户组 > 终端类型")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用接口删除所有测试VLAN授权规则")
        return "\n".join(lines)

    # ── 001~006: 认证触发 + VLAN 断言 ──

    # 前置：创建区域
    has_seven_level = '七级' in steps
    if has_seven_level:
        lines.append(f"{n}. 调用区域管理接口，在站点1下创建七级区域1和七级区域2")
    else:
        lines.append(f"{n}. 调用区域管理接口，在站点1下创建区域1和区域2")
    n += 1

    # 前置：设备纳管
    lines.append(f"{n}. 调用设备纳管接口，将接入设备分别纳管到区域1和区域2，断言协议状态正常")
    n += 1

    # 创建VLAN授权规则
    auth_type = _detect_auth_type(steps)
    vlan_rule = _describe_vlan_rule(steps)
    lines.append(f"{n}. 调用认证VLAN授权配置接口，授权类型：{auth_type}，{vlan_rule}")
    n += 1

    # 前置：创建用户/MAC记录
    if '用户名' in auth_type or '用户名' in steps:
        lines.append(f"{n}. 调用用户管理接口，创建用户1和用户2，确认用户存在")
        n += 1
    elif '用户mac' in auth_type.lower() or 'mac' in str(steps).lower()[:50]:
        lines.append(f"{n}. 调用用户管理接口，确认MAC1和MAC2用户已存在")
        n += 1

    # 特殊前置：哑终端先接入场景（005）
    if num == '005':
        lines.append(f"{n}. 模拟AP1和AP2在无MAC认证记录时尝试接入，调用认证日志接口断言认证失败")
        n += 1
        lines.append(f"{n}. 调用哑终端MAC认证列表接口，为AP1和AP2新增无感认证记录")
        n += 1

    # 触发认证
    auth_method = _detect_trigger_method(steps, num)
    lines.append(f"{n}. 调用模拟认证接口，{auth_method}")
    n += 1

    # 断言 VLAN 下发
    vlan_assert = _describe_vlan_assert(name, expect, steps)
    lines.append(f"{n}. 调用在线用户查询接口，断言{vlan_assert}")
    n += 1

    # 重新认证场景（003/004/005）
    if num in ('003', '004', '005'):
        lines.append(f"{n}. 调用模拟断开接口，断开连接后重新触发认证")
        n += 1
        lines.append(f"{n}. 调用在线用户查询接口，断言重新认证后VLAN授权不变")
        n += 1

    # 额外验证：认证模板（002）
    if num == '002':
        lines.append(f"{n}. 确认用户认证模板已勾选「允许WEB认证VLAN授权」选项（调用认证模板查询接口）")
        n += 1

    lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户/VLAN授权规则/区域/设备纳管")
    return "\n".join(lines)


def _detect_auth_type(steps):
    if '用户名' in steps:
        return '用户名'
    if '用户组' in steps:
        return '用户组'
    if '用户mac' in steps.lower() or '用户MAC' in steps:
        return '用户MAC'
    if '终端类型' in steps:
        return '终端类型'
    return '用户名'


def _describe_vlan_rule(steps):
    if 'vlan88' in steps and 'vlan110' in steps:
        return '区域1配置两条授权规则（→vlan88 和 →vlan110），断言配置成功'
    if 'vlan102' in steps:
        return '区域1/区域2分别配置多条授权规则（→vlan88/110/102），断言配置成功'
    return '配置各区域VLAN授权规则，断言配置成功'


def _detect_trigger_method(steps, num):
    if num == '002':
        return '用户1和用户2通过区域1下的接入设备发起portal认证'
    if num in ('003', '005'):
        return '用户1和用户2通过区域1下的接入设备发起portal+MAB认证'
    if num in ('004',):
        return 'AP1和AP2通过区域1下的接入设备发起无感MAB认证'
    if '有线' in steps or num == '006':
        return '用户1和用户2通过区域1下的接入设备发起有线802.1x认证'
    return '用户通过区域1下的接入设备发起802.1x认证'


def _describe_vlan_assert(name, expect, steps):
    if 'vlan88' in expect and 'vlan110' in expect:
        return '用户1授权vlan为88、用户2授权vlan为110，各自获取对应子网IP地址，认证响应报文中Tunnel-Private-Group-ID字段值正确'
    if 'vlan88' in expect:
        return 'VLAN授权下发正确，用户获取对应子网IP地址'
    return 'VLAN授权下发符合预期'


# ══════════════════════════════════════════════════════
# 脚本名称
# ══════════════════════════════════════════════════════

def generate_script_name(case_id, name, expect):
    num = case_id.split('-')[-1] if '-' in case_id else ''

    if num == '001':
        return '基于区域802.1x认证-调用区域/设备纳管/VLAN授权配置接口-触发认证-断言VLAN正确下发'
    if num == '002':
        return '基于区域portal认证-调用区域/设备纳管/VLAN授权配置接口-触发portal认证-断言VLAN正确下发'
    if num == '003':
        return '基于区域portal+MAB认证-调用VLAN授权配置接口-触发MAB认证及重新认证-断言VLAN持续正确'
    if num == '004':
        return '哑终端基于区域MAB认证-调用VLAN授权配置接口-触发无感认证及重认证-断言VLAN正确下发'
    if num == '005':
        return '哑终端先接入后加MAC记录-调用VLAN授权配置和MAC记录接口-断言加记录前失败加记录后成功'
    if num == '006':
        return '有线802.1x认证-调用区域/设备纳管/VLAN授权配置接口-触发有线认证-断言VLAN正确下发'
    if num == '007':
        return '认证VLAN授权支持站点隔离-调用多站点授权CRUD接口-断言站点间数据互不影响'
    if num == '008':
        return 'VLAN授权优先级-调用四类授权配置接口-依次触发认证删规则-断言优先级MAC>用户名>用户组>终端类型'
    return name[:60]


def determine_directory(test_point, name, num):
    if num in ('001', '002', '003', '004', '005', '006'):
        return 'VLAN授权优化/认证触发-VLAN下发'
    if num == '007':
        return 'VLAN授权优化/站点管理'
    if num == '008':
        return 'VLAN授权优化/授权优先级'
    return 'VLAN授权优化/其他'


# ══════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════

def main():
    print("📖 读取飞书表格 W9QybU ...")
    cases = read_sheet()
    print(f"   读取到 {len(cases)} 条用例")

    print("🔍 分析用例...")
    results = []
    for i, case in enumerate(cases, start=1):
        cid = case.get('用例编号', f'vlan授权优化-{i:03d}')
        test_point = case.get('测试点描述', '')
        name = case.get('用例名称', '') or ''
        desc = case.get('用例描述', '') or ''
        precondition = case.get('预置条件', '') or ''
        steps = case.get('测试步骤', '') or ''
        expect = case.get('期望结果', '') or ''

        num = cid.split('-')[-1] if '-' in cid else str(i).zfill(3)
        automatable, no_auto_reason = classify_case(cid, name, steps, expect)
        auto_steps = generate_automation_steps(cid, name, precondition, steps, expect)
        script_name = generate_script_name(cid, name, expect)
        directory = determine_directory(test_point, name, num)

        results.append({
            '用例编号': cid,
            '测试点描述': test_point,
            '用例名称': name,
            '用例描述': desc,
            '预置条件': precondition,
            '测试步骤': steps,
            '期望结果': expect,
            '是否可自动化': automatable,
            '不可自动化原因': no_auto_reason,
            '自动化关键步骤': auto_steps,
            '脚本名称': script_name,
            '目录分类': directory,
        })

    result_file = os.path.join(WORKSPACE, 'w9qybu_analysis_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"   分析结果已保存: {result_file}")

    report = generate_report(results)
    report_file = os.path.join(WORKSPACE, 'w9qybu_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 分析报告已生成: {report_file}")

    print("✅ 分析完成（回写请运行 write_w9qybu_to_lark.py）")


def generate_report(results):
    lines = []
    lines.append("# 认证VLAN授权优化用例自动化分析报告\n")
    lines.append("**分析日期**: 2026-03-05  ")
    lines.append(f"**用例总数**: {len(results)}  ")
    auto_yes = sum(1 for r in results if r['是否可自动化'] == '是')
    auto_no = sum(1 for r in results if r['是否可自动化'] == '否')
    lines.append(f"**可自动化**: {auto_yes} | **不可自动化**: {auto_no}\n")

    lines.append("---\n")
    lines.append("## 📁 建议目录结构\n```")
    dirs = {}
    for r in results:
        dirs.setdefault(r['目录分类'], []).append(f"{r['用例编号']} {r['用例名称'][:60]}")
    for d in sorted(dirs):
        lines.append(f"{d}/")
        for c in dirs[d]:
            lines.append(f"    ├── {c}")
    lines.append("```\n")

    lines.append("---\n")
    lines.append("## 📊 用例分析汇总\n")
    lines.append("| 编号 | 用例名称 | 可自动化 | 脚本名称 |")
    lines.append("|------|---------|---------|---------|")
    for r in results:
        lines.append(f"| {r['用例编号']} | {r['用例名称'][:50]} | {r['是否可自动化']} | {r['脚本名称'][:70]} |")
    lines.append("")

    lines.append("---\n")
    lines.append("## 📋 详细分析\n")
    for r in results:
        lines.append(f"### {r['用例编号']} {r['用例名称']}\n")
        lines.append(f"**是否可自动化**: {r['是否可自动化']}  ")
        if r['不可自动化原因']:
            lines.append(f"**不可自动化原因**: {r['不可自动化原因']}  ")
        lines.append(f"**脚本名称**: `{r['脚本名称']}`  ")
        lines.append(f"**目录**: `{r['目录分类']}`\n")
        lines.append("**自动化关键步骤**:\n```")
        lines.append(r['自动化关键步骤'])
        lines.append("```\n")
        if r['期望结果']:
            lines.append("**期望结果**:\n```")
            lines.append(r['期望结果'])
            lines.append("```\n")
        lines.append("---\n")

    lines.append("## 💡 自动化建议\n")
    for r in results:
        if r['是否可自动化'] == '是':
            lines.append(f"- **{r['用例编号']}** {r['用例名称'][:60]}")
    lines.append("\n---\n")
    lines.append("**维护者**: 魏斌  ")
    lines.append("**生成时间**: 2026-03-05")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
