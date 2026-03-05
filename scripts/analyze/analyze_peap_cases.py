#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PEAP用例自动化分析脚本
读取飞书表格 → 分析自动化可行性 → 生成编号/关键步骤/脚本名称 → 回写飞书 → 输出报告
"""

import sys
import os
import json
import re

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-writer'))

from lark_sheet_reader import LarkSheetReader
from lark_sheet_writer import LarkSheetWriter

# ── 常量 ──────────────────────────────────────────────
LARK_APP_ID = "cli_a83faf50a228900e"
LARK_APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SHEET_URL = "https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=gBtCcn"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "gBtCcn"

# 公共步骤引用
REF_LOGIN_ADMIN = "引用51401"  # 登录管理端

WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')

# ── 分析规则 ──────────────────────────────────────────

def classify_case(name, steps, expect):
    """根据用例名称/步骤/预期判断自动化可行性，返回 (是否可自动化, 原因)"""
    name_lower = name.lower()

    # ── 需要物理设备的场景 → 否 ──
    device_keywords = [
        'win11', 'macos', '小米手机', 'oppo手机', 'ios系统', 'ipad',
        'android pad', 'android pad', '鸿蒙系统'
    ]
    for kw in device_keywords:
        if kw in name_lower:
            return '否', f'需要物理设备({kw})进行真实无线认证，无法通过API模拟'

    # ── 自助端操作 → 部分 ──
    if '自助端' in name:
        return '部分', '自助端下线操作需要自助端UI/API，管理端查询可通过API验证'

    # ── 证书相关 → 部分 ──
    if '证书' in name:
        return '部分', '证书上传/查看可通过管理端API，但证书实际生效需要真实认证流程验证'

    # ── 1x协议说明/选择 → 是 ──
    if '1x' in name_lower and ('说明' in name or '选择' in name):
        return '是', '协议配置项的查询和设置可通过管理端API完成'

    # ── 主要认证流程用例（PEAP/EAP-TTLS + 本地/LDAP） → 部分 ──
    auth_keywords = ['认证', 'ldap', 'peap', '校验', '加密', '密码错误', '账号不存在', '账号冲突']
    for kw in auth_keywords:
        if kw in name_lower or kw.upper() in name:
            return '部分', '管理端配置/查询/断言可通过API自动化；无线认证触发需物理终端或仿真工具'

    # 默认
    return '部分', '需进一步评估具体步骤'


def generate_automation_steps(name, precondition, steps, expect):
    """生成自动化关键步骤描述"""
    lines = []
    step_num = 1

    # ── 前置: 登录管理端 ──
    lines.append(f"{step_num}. 登录管理端 - {REF_LOGIN_ADMIN}")
    step_num += 1

    # ── 前置: 根据预置条件生成配置步骤 ──
    if precondition:
        pre_items = [p.strip() for p in re.split(r'\n', precondition) if p.strip()]
        for item in pre_items:
            item_clean = re.sub(r'^\d+[\.\、]', '', item).strip()
            if not item_clean:
                continue
            if 'win10' in item_clean.lower() or 'win11' in item_clean.lower() or '电脑' in item_clean:
                lines.append(f"{step_num}. 准备测试终端: {item_clean}")
            elif 'LDAP' in item_clean or 'ldap' in item_clean:
                lines.append(f"{step_num}. 配置LDAP认证源 - 调用认证源配置API")
            elif '认证' in item_clean and '配置' in item_clean:
                lines.append(f"{step_num}. 配置认证参数: {item_clean} - 调用认证配置API")
            elif '证书' in item_clean:
                lines.append(f"{step_num}. 配置证书: {item_clean} - 调用证书管理API")
            else:
                lines.append(f"{step_num}. 前置配置: {item_clean}")
            step_num += 1

    # ── 开户生成测试数据 ──
    if any(kw in name for kw in ['本地用户', '本地账户']):
        lines.append(f"{step_num}. 开户生成测试数据 - 创建本地认证用户（调用用户管理API）")
        step_num += 1
    elif 'LDAP' in name:
        lines.append(f"{step_num}. 开户生成测试数据 - 确保LDAP用户存在（调用LDAP用户查询API）")
        step_num += 1

    # ── 核心测试步骤 ──
    if steps:
        step_items = [s.strip() for s in re.split(r'\n', steps) if s.strip()]
        for item in step_items:
            item_clean = re.sub(r'^\d+[\.\、]', '', item).strip()
            if not item_clean:
                continue
            if '连接1x信号' in item_clean or '连接' in item_clean and '信号' in item_clean:
                lines.append(f"{step_num}. 触发802.1X认证（物理终端连接或仿真工具触发）")
            elif '认证' in item_clean and ('用户' in item_clean or '进行' in item_clean):
                lines.append(f"{step_num}. 执行用户认证: {item_clean}")
            elif '查看' in item_clean and '在线' in item_clean:
                lines.append(f"{step_num}. 查询在线用户列表 - 调用在线用户查询API并断言用户状态")
            elif '断开' in item_clean or '下线' in item_clean:
                if '自助' in item_clean:
                    lines.append(f"{step_num}. 自助端下线操作 - 调用自助端下线API")
                elif '管理端' in item_clean:
                    lines.append(f"{step_num}. 管理端强制下线 - 调用管理端下线API")
                else:
                    lines.append(f"{step_num}. 终端断开连接（物理断开或仿真断开）")
            elif '自助' in item_clean:
                lines.append(f"{step_num}. 自助端操作: {item_clean} - 调用自助端API")
            elif '查看' in item_clean or '验证' in item_clean:
                lines.append(f"{step_num}. 查询并断言: {item_clean} - 调用管理端查询API")
            else:
                lines.append(f"{step_num}. {item_clean}")
            step_num += 1

    # ── 断言 ──
    if expect:
        expect_items = [e.strip() for e in re.split(r'\n', expect) if e.strip()]
        assertions = []
        for item in expect_items:
            item_clean = re.sub(r'^\d+[\.\、]', '', item).strip()
            if item_clean:
                assertions.append(item_clean)
        if assertions:
            lines.append(f"{step_num}. 断言预期结果: " + "; ".join(assertions))
            step_num += 1

    # ── 清理 ──
    lines.append(f"{step_num}. 清理测试数据 - 删除测试用户/恢复认证配置")

    return "\n".join(lines)


def generate_script_name(name, steps, expect):
    """生成脚本标题：简要覆盖 前置-测试-预期 的关键点"""
    # 提取关键场景标识
    parts = []

    # 前置关键词
    if 'PEAP' in name:
        parts.append('PEAP')
    elif 'EAP-TTLS' in name or 'TTLS' in name:
        parts.append('EAP-TTLS')

    if 'LDAP' in name:
        if '登录' in name and '身份校验' in name:
            parts.append('LDAP登录校验')
        elif '查询' in name and '身份校验' in name:
            parts.append('LDAP查询校验')
        else:
            parts.append('LDAP用户')
    elif '本地' in name:
        parts.append('本地用户')

    # 测试动作
    if '主动下线' in name:
        parts.append('主动下线')
    elif '自助端下线' in name:
        parts.append('自助端下线')
    elif '管理端下线' in name:
        parts.append('管理端下线')
    elif '自助功能' in name:
        parts.append('自助功能验证')
    elif '密码错误' in name:
        parts.append('密码错误')
    elif '账号不存在' in name:
        parts.append('账号不存在')
    elif '账号冲突' in name:
        parts.append('账号冲突')
    elif '不加密' in name:
        parts.append('明文存储')
    elif '加密存储' in name:
        parts.append('加密存储')
    elif 'MD4' in name:
        parts.append('MD4加密')
    elif 'MD5 16' in name:
        parts.append('MD5-Hex')
    elif 'MD5 Base64' in name:
        parts.append('MD5-Base64')
    elif '不启用' in name:
        parts.append('不校验密码')
    elif '每次认证' in name:
        parts.append('每次LDAP校验')
    elif '定期' in name:
        parts.append('定期LDAP校验')
    elif '不对接LDAP' in name and '本地' in name:
        parts.append('无LDAP本地认证')
    elif '不对接LDAP' in name and 'LDAP' in name:
        parts.append('无LDAP源LDAP认证失败')
    elif '证书文件限制' in name:
        parts.append('证书文件格式校验')
    elif '证书上传' in name:
        parts.append('证书上传功能')
    elif '证书详情' in name:
        parts.append('证书详情查看')
    elif '1x' in name.lower() and '说明' in name:
        parts.append('协议说明展示')
    elif '1x' in name.lower() and '选择' in name:
        parts.append('协议切换')

    # 多平台
    platform_map = {
        'win11': 'Win11', 'macos': 'macOS', '小米手机': '小米',
        'oppo手机': 'OPPO', 'ios系统': 'iOS', 'ipad': 'iPad',
        'android pad': 'AndroidPad', '鸿蒙系统': '鸿蒙'
    }
    for kw, label in platform_map.items():
        if kw in name.lower():
            parts.append(f'{label}兼容性')
            break

    # 预期关键点
    if expect:
        if '认证成功' in expect:
            parts.append('验证认证成功')
        elif '认证失败' in expect:
            parts.append('验证认证失败')
        elif '在线' in expect and '离线' in expect:
            parts.append('验证上下线状态')
        elif '在线' in expect:
            parts.append('验证在线状态')

    if not parts:
        parts.append(name[:20])

    return '_'.join(parts)


def determine_directory(name):
    """根据用例名称确定所属目录分类"""
    if any(kw in name for kw in ['win11', 'macOS', 'macos', '小米手机', 'oppo手机',
                                   'IOS系统', 'iOS', 'iPad', 'ipad', 'android',
                                   'Android', '鸿蒙']):
        return 'PEAP认证/多平台兼容性'
    if '证书' in name:
        return 'PEAP认证/证书管理'
    if '1x' in name.lower():
        return 'PEAP认证/协议配置'

    prefix = ''
    if 'PEAP' in name:
        prefix = 'PEAP认证/PEAP协议'
    else:
        prefix = 'PEAP认证/EAP-TTLS协议'

    if '本地用户' in name or '本地账户' in name:
        return f'{prefix}/本地用户认证'
    if '登录LDAP服务器' in name:
        return f'{prefix}/LDAP校验方式/登录LDAP服务器'
    if '查询LDAP用户信息' in name:
        return f'{prefix}/LDAP校验方式/查询LDAP用户信息'
    if '认证校验密码' in name:
        return f'{prefix}/认证校验密码'
    if 'LDAP' in name:
        return f'{prefix}/LDAP用户认证'
    if '自助' in name:
        return f'{prefix}/自助功能'
    if '密码错误' in name or '账号不存在' in name or '账号冲突' in name:
        return f'{prefix}/异常场景'
    if '不对接LDAP' in name:
        return f'{prefix}/无LDAP对接'

    return prefix


# ── 主流程 ──────────────────────────────────────────

def main():
    # 1. 读取飞书表格
    print("📖 读取飞书表格...")
    reader = LarkSheetReader(LARK_APP_ID, LARK_APP_SECRET)
    cases = reader.read_from_url(SHEET_URL)
    print(f"   读取到 {len(cases)} 条用例")

    # 2. 分析每条用例
    print("🔍 分析用例...")
    analysis_results = []
    for i, case in enumerate(cases, start=1):
        case_id = f"PEAP-{i:03d}"
        name = case.get('用例名称', '') or ''
        desc = case.get('用例描述', '') or ''
        precondition = case.get('预置条件', '') or ''
        steps = case.get('测试步骤', '') or ''
        expect = case.get('期望结果', '') or ''

        automatable, reason = classify_case(name, steps, expect)
        auto_steps = generate_automation_steps(name, precondition, steps, expect)
        script_name = generate_script_name(name, steps, expect)
        directory = determine_directory(name)

        analysis_results.append({
            '用例编号': case_id,
            '用例名称': name,
            '用例描述': desc,
            '预置条件': precondition,
            '测试步骤': steps,
            '期望结果': expect,
            '是否可自动化': automatable,
            '自动化分析原因': reason,
            '自动化关键步骤': auto_steps,
            '脚本名称': script_name,
            '目录分类': directory,
        })

    # 3. 保存分析结果到本地 JSON
    result_file = os.path.join(WORKSPACE, 'peap_analysis_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    print(f"   分析结果已保存: {result_file}")

    # 4. 生成 Markdown 报告
    report = generate_report(analysis_results)
    report_file = os.path.join(WORKSPACE, 'peap_automation_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 分析报告已生成: {report_file}")

    # 5. 回写飞书表格
    print("✍️  回写飞书表格...")
    write_to_lark(analysis_results)
    print("✅ 全部完成！")


def write_to_lark(results):
    """回写分析结果到飞书表格"""
    writer = LarkSheetWriter(LARK_APP_ID, LARK_APP_SECRET)
    writer.get_access_token()

    # 获取表头确定列位置
    headers = writer.get_sheet_headers(SPREADSHEET_TOKEN, SHEET_ID)
    print(f"   表头: {headers}")

    # 找到各列的索引（0-based）
    col_map = {}
    for i, h in enumerate(headers):
        col_map[h] = i

    col_case_id = col_map.get('用例编号', 0)
    col_automatable = col_map.get('是否可自动化', 6)
    col_script_name = col_map.get('脚本名称', 8)

    # 检查是否有"自动化关键步骤"列，如果没有需要提示
    col_auto_steps = col_map.get('自动化关键步骤')

    # 逐行写入：用例编号、是否可自动化、脚本名称
    for i, result in enumerate(results):
        row_num = i + 2  # 表格从第2行开始（第1行是表头）

        # 写用例编号  (A列 = col 1)
        col_letter_id = writer._col_number_to_letter(col_case_id + 1)
        range_id = f"{SHEET_ID}!{col_letter_id}{row_num}:{col_letter_id}{row_num}"
        r = writer._write_range(SPREADSHEET_TOKEN, range_id, [[result['用例编号']]])
        if not r['success']:
            print(f"   ⚠️ 写入用例编号失败 行{row_num}: {r.get('error')}")

        # 写是否可自动化
        col_letter_auto = writer._col_number_to_letter(col_automatable + 1)
        range_auto = f"{SHEET_ID}!{col_letter_auto}{row_num}:{col_letter_auto}{row_num}"
        r = writer._write_range(SPREADSHEET_TOKEN, range_auto, [[result['是否可自动化']]])
        if not r['success']:
            print(f"   ⚠️ 写入是否可自动化失败 行{row_num}: {r.get('error')}")

        # 写脚本名称
        col_letter_script = writer._col_number_to_letter(col_map.get('脚本名称', 8) + 1)
        range_script = f"{SHEET_ID}!{col_letter_script}{row_num}:{col_letter_script}{row_num}"
        r = writer._write_range(SPREADSHEET_TOKEN, range_script, [[result['脚本名称']]])
        if not r['success']:
            print(f"   ⚠️ 写入脚本名称失败 行{row_num}: {r.get('error')}")

        # 如果有自动化关键步骤列就写入
        if col_auto_steps is not None:
            col_letter_steps = writer._col_number_to_letter(col_auto_steps + 1)
            range_steps = f"{SHEET_ID}!{col_letter_steps}{row_num}:{col_letter_steps}{row_num}"
            r = writer._write_range(SPREADSHEET_TOKEN, range_steps, [[result['自动化关键步骤']]])
            if not r['success']:
                print(f"   ⚠️ 写入自动化关键步骤失败 行{row_num}: {r.get('error')}")

    print(f"   已回写 {len(results)} 行")


def generate_report(results):
    """生成 Markdown 分析报告"""
    lines = []
    lines.append("# PEAP认证用例自动化分析报告\n")
    lines.append(f"**分析日期**: 2026-03-05  ")
    lines.append(f"**用例总数**: {len(results)}  ")

    # 统计
    auto_yes = sum(1 for r in results if r['是否可自动化'] == '是')
    auto_partial = sum(1 for r in results if r['是否可自动化'] == '部分')
    auto_no = sum(1 for r in results if r['是否可自动化'] == '否')
    lines.append(f"**可自动化**: {auto_yes} | **部分可自动化**: {auto_partial} | **不可自动化**: {auto_no}\n")

    # ── 目录结构 ──
    lines.append("---\n")
    lines.append("## 📁 建议目录结构\n")
    lines.append("```")
    dirs = {}
    for r in results:
        d = r['目录分类']
        if d not in dirs:
            dirs[d] = []
        dirs[d].append(f"{r['用例编号']} {r['用例名称']}")

    # 按目录排序输出树形结构
    sorted_dirs = sorted(dirs.keys())
    for d in sorted_dirs:
        lines.append(f"{d}/")
        for case in dirs[d]:
            lines.append(f"    ├── {case}")
    lines.append("```\n")

    # ── 汇总表格 ──
    lines.append("---\n")
    lines.append("## 📊 用例分析汇总\n")
    lines.append("| 编号 | 用例名称 | 是否可自动化 | 脚本名称 | 目录分类 |")
    lines.append("|------|---------|------------|---------|---------|")
    for r in results:
        lines.append(f"| {r['用例编号']} | {r['用例名称']} | {r['是否可自动化']} | {r['脚本名称']} | {r['目录分类']} |")
    lines.append("")

    # ── 详细分析 ──
    lines.append("---\n")
    lines.append("## 📋 详细分析\n")
    for r in results:
        lines.append(f"### {r['用例编号']} {r['用例名称']}\n")
        lines.append(f"**是否可自动化**: {r['是否可自动化']}  ")
        lines.append(f"**原因**: {r['自动化分析原因']}  ")
        lines.append(f"**脚本名称**: `{r['脚本名称']}`  ")
        lines.append(f"**目录**: `{r['目录分类']}`\n")

        if r['预置条件']:
            lines.append(f"**预置条件**:")
            lines.append(f"```")
            lines.append(r['预置条件'])
            lines.append(f"```\n")

        lines.append(f"**自动化关键步骤**:")
        lines.append(f"```")
        lines.append(r['自动化关键步骤'])
        lines.append(f"```\n")

        if r['期望结果']:
            lines.append(f"**期望结果**:")
            lines.append(f"```")
            lines.append(r['期望结果'])
            lines.append(f"```\n")

        lines.append("---\n")

    # ── 自动化建议 ──
    lines.append("## 💡 自动化建议\n")
    lines.append("### 可完全自动化的用例")
    lines.append("以下用例可直接通过管理端API完成端到端自动化：\n")
    for r in results:
        if r['是否可自动化'] == '是':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']}")
    lines.append("")

    lines.append("### 部分可自动化的用例")
    lines.append("以下用例的管理端配置/查询/断言部分可以自动化，核心认证触发需物理终端或仿真工具：\n")
    for r in results:
        if r['是否可自动化'] == '部分':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']} — {r['自动化分析原因']}")
    lines.append("")

    lines.append("### 不可自动化的用例")
    lines.append("以下用例需要特定物理设备，建议保持手工测试：\n")
    for r in results:
        if r['是否可自动化'] == '否':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']} — {r['自动化分析原因']}")
    lines.append("")

    lines.append("---\n")
    lines.append("**维护者**: 魏斌  ")
    lines.append("**生成时间**: 2026-03-05")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
