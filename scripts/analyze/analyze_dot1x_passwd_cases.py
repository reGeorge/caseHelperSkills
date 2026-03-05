#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
802.1x密码复杂度用例自动化分析脚本
读取飞书表格 UmATpA → 分析自动化可行性 → 生成脚本名称/自动化步骤 → 回写飞书 → 输出报告

sheet 列布局 (A-J 已有数据):
  A=测试点描述  B=用例包名称  C=用例标签  D=用例编号  E=回归测试
  F=用例名称  G=用例描述  H=预置条件  I=测试步骤  J=期望结果
  K=是否可自动化(新增)  L=不可自动化原因(新增)  M=脚本名称(新增)
"""

import sys
import os
import json
import re
import requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-writer'))

from lark_sheet_reader import LarkSheetReader

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "UmATpA"
BASE_URL = "https://open.feishu.cn/open-apis"
REF_LOGIN_ADMIN = "引用51401"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')


# ══════════════════════════════════════════════════════
# 读取飞书表格（直接API，处理富文本单元格）
# ══════════════════════════════════════════════════════

def cell_text(cell):
    """提取单元格文本，兼容富文本格式"""
    if cell is None:
        return ''
    if isinstance(cell, str):
        return cell.strip()
    if isinstance(cell, list):
        return ''.join(
            seg['text'] for seg in cell
            if isinstance(seg, dict) and 'text' in seg
        ).strip()
    return str(cell).strip()


def read_sheet():
    """读取 UmATpA 表格，返回 List[Dict]"""
    reader = LarkSheetReader(APP_ID, APP_SECRET)
    token = reader.get_access_token()
    hdrs = {'Authorization': 'Bearer ' + token}

    # 读最多300行（远超实际数量）
    range_str = SHEET_ID + '!A1:L300'
    url = BASE_URL + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values/' + range_str
    r = requests.get(url, headers=hdrs)
    raw_rows = r.json().get('data', {}).get('valueRange', {}).get('values', [])

    # 处理表头
    header_row = raw_rows[0]
    col_names = [cell_text(h) for h in header_row]
    # A列有长换行标题，简化为 "测试点描述"
    col_names[0] = '测试点描述'

    cases = []
    for row in raw_rows[1:]:
        if not any(cell_text(c) for c in row):
            continue
        row_dict = {}
        for i, h in enumerate(col_names):
            row_dict[h] = cell_text(row[i]) if i < len(row) else ''
        if row_dict.get('用例编号', '').startswith('RG-'):
            cases.append(row_dict)

    return cases


# ══════════════════════════════════════════════════════
# 分类：是/否 + 原因
# ══════════════════════════════════════════════════════

# 不可自动化的测试点（UI展示/前端校验/定时任务）
_NO_AUTO_POINTS = {
    '密码安全管理页面新增配置组展示': '纯UI展示校验：页面新增配置组及按钮显示属于前端渲染，不适合API自动化',
    '定期修改周期输入参数校验':       '前端输入校验：定期修改周期输入框前端自动纠正行为，不适合API自动化',
    '提前短信通知时间输入参数比较':    '前端输入校验：提前短信通知时间与定期修改周期的大小比较校验，属于前端行为',
    '提前短信通知时间输入参数校验':    '前端输入校验：提前短信通知时间输入框前端校验行为，不适合API自动化',
    '802.1x密码校验短信通知配置展示': '纯UI展示校验：消息配置页面展示新增配置组属于前端渲染，不适合API自动化',
    '定时任务':                       '依赖系统时钟定时触发（每日21点发短信/密码过期判断），API自动化不适合等待真实时钟',
}


def classify_case(test_point, name, steps, expect):
    """返回 (是否可自动化: '是'|'否', 不可自动化原因: str)"""
    for kw, reason in _NO_AUTO_POINTS.items():
        if kw in test_point:
            return '否', reason
    return '是', ''


# ══════════════════════════════════════════════════════
# 解析认证组合用例配置状态
# ══════════════════════════════════════════════════════

def parse_case_config(name):
    """从用例名称中解析认证配置状态，返回 dict"""
    cfg = {}

    # 登录类型
    if '非首次登录' in name:
        cfg['login_type'] = '非首次'
    elif '首次登录' in name:
        cfg['login_type'] = '首次'
    else:
        cfg['login_type'] = None

    # 密码策略符合性
    cfg['meets_policy'] = '不符合密码策略' not in name and '符合密码策略' in name

    # 三个强制策略按钮
    cfg['first_enforce_on'] = '关闭首次登录用户强制修改密码' not in name and \
                               ('开启首次登录用户强制修改密码' in name or '首次登录用户强制修改密码' in name)
    cfg['strength_enforce_on'] = ('关闭对未通过密码强度' not in name) and \
                                  ('开启对未通过密码强度' in name)
    cfg['periodic_enforce_on'] = ('关闭定时强制' not in name) and \
                                  ('开启定时强制' in name or '开启启用定期修改' in name)

    # SMS 是否配置好
    cfg['sms_ok'] = '未获取到用户手机号' not in name and \
                    '未配置' not in name and \
                    '没有配置' not in name

    # 第三方用户类型（第三方不受密码策略约束）
    cfg['third_party'] = '第三方' in name or 'AD' in name or 'RADIUS' in name or 'Voucher' in name

    return cfg


def extract_auth_result(expect):
    """从期望结果中提取认证结论"""
    if not expect:
        return ''
    if '认证成功' in expect and '认证失败' not in expect:
        return '认证成功'
    if '认证失败' in expect:
        for kw in ['用户首次登录需修改密码', '首次登录需修改密码', '未通过密码强度检测', '密码已过期', '密码已过期']:
            if kw in expect:
                return '认证失败-' + kw
        return '认证失败'
    return ''


# ══════════════════════════════════════════════════════
# 脚本名称生成
# ══════════════════════════════════════════════════════

def generate_script_name(test_point, name, expect):
    """生成脚本名称"""

    # ── 不可自动化用例 ──
    for kw in _NO_AUTO_POINTS:
        if kw in test_point:
            if '展示' in test_point or '配置展示' in test_point:
                short = '密码安全管理' if '密码安全管理' in test_point else '消息配置'
                return '不可自动化-' + short + '页面新增配置组UI展示检查'
            elif '输入参数' in test_point:
                return '不可自动化-前端输入框参数校验行为'
            elif '定时任务' in test_point:
                return '不可自动化-定时任务依赖系统时钟无法API触发'
            return '不可自动化-' + test_point[:30]

    # ── 认证组合用例 ──
    cfg = parse_case_config(name)
    auth_result = extract_auth_result(expect)

    parts = []

    # 登录类型
    if cfg.get('login_type'):
        parts.append(cfg['login_type'] + '登录')

    # 密码策略
    parts.append('符合策略' if cfg.get('meets_policy') else '不符合策略')

    # 三按钮状态
    enforcements = []
    if cfg.get('first_enforce_on'):
        enforcements.append('首次登录强制开')
    if cfg.get('strength_enforce_on'):
        enforcements.append('强度检测强制开')
    if cfg.get('periodic_enforce_on'):
        enforcements.append('定时强制开')
    if enforcements:
        parts.append('+'.join(enforcements))
    else:
        parts.append('三策略均关')

    # 第三方用户
    if cfg.get('third_party'):
        parts.append('第三方用户')

    # 接口动作
    parts.append('调用配置接口设策略-触发1x认证')

    # 断言结果
    if auth_result:
        parts.append('断言' + auth_result)
    else:
        parts.append('断言认证结果符合预期')

    return '-'.join(parts)


# ══════════════════════════════════════════════════════
# 自动化关键步骤生成
# ══════════════════════════════════════════════════════

def generate_automation_steps(test_point, name, precondition, steps, expect):
    """生成面向API的自动化关键步骤"""

    lines = []
    n = 1

    # ── 不可自动化用例 ──
    for kw in _NO_AUTO_POINTS:
        if kw in test_point:
            if '展示' in test_point or '配置展示' in test_point:
                lines.append(f"{n}. 纯页面UI展示校验，不适合API自动化（需要UI自动化框架）")
            elif '输入参数' in test_point:
                lines.append(f"{n}. 前端输入框边界值/格式校验，属于前端行为，不适合API自动化")
            elif '定时任务' in test_point:
                lines.append(f"{n}. 定时任务依赖系统每日特定时间点触发，无法通过API模拟时钟推进，不适合API自动化")
            else:
                lines.append(f"{n}. 不适合API自动化")
            return "\n".join(lines)

    # ── 认证组合用例 ──
    cfg = parse_case_config(name)
    auth_result = extract_auth_result(expect)

    # 1. 登录管理端
    lines.append(f"{n}. 登录管理端 - {REF_LOGIN_ADMIN}")
    n += 1

    # 2. 配置密码策略（从预置条件解析）
    if precondition:
        if '密码策略' in precondition or '大写' in precondition or '小写' in precondition:
            lines.append(f"{n}. 调用密码策略配置接口，设置密码复杂度要求（首字母大写、包含小写字母、数字、特殊字符，长度3-30）")
            n += 1

    # 3. 三个强制策略配置
    if cfg.get('first_enforce_on'):
        sms_note = ''
        if '返回认证失败+短信通知' in name and cfg.get('sms_ok'):
            sms_note = '，强制处理方式设为"返回认证失败+短信通知"'
        elif '返回认证失败+短信通知' in name:
            sms_note = '，强制处理方式设为"返回认证失败+短信通知"（注：短信网关/模板可能未配置）'
        else:
            sms_note = '，强制处理方式设为"返回认证失败"'
        lines.append(f"{n}. 调用密码安全管理配置接口，开启「首次登录用户强制修改密码」按钮{sms_note}")
        n += 1
    else:
        lines.append(f"{n}. 调用密码安全管理配置接口，关闭「首次登录用户强制修改密码」按钮")
        n += 1

    if cfg.get('strength_enforce_on'):
        sms_note = ''
        if '返回认证失败+短信通知' in name and cfg.get('sms_ok'):
            sms_note = '，强制处理方式设为"返回认证失败+短信通知"'
        else:
            sms_note = '，强制处理方式设为"返回认证失败"'
        lines.append(f"{n}. 调用密码安全管理配置接口，开启「对未通过密码强度检测的用户进行强制处理」按钮{sms_note}")
        n += 1
    else:
        lines.append(f"{n}. 调用密码安全管理配置接口，关闭「对未通过密码强度检测的用户进行强制处理」按钮")
        n += 1

    if cfg.get('periodic_enforce_on'):
        sms_note = ''
        if '返回认证失败+短信通知' in name and cfg.get('sms_ok'):
            sms_note = '，强制处理方式设为"返回认证失败+短信通知"'
        else:
            sms_note = '，强制处理方式设为"返回认证失败"'
        lines.append(f"{n}. 调用密码安全管理配置接口，开启「启用定期修改密码」按钮{sms_note}")
        n += 1
    else:
        lines.append(f"{n}. 调用密码安全管理配置接口，关闭「启用定期修改密码」按钮")
        n += 1

    # 4. 创建测试用户
    if cfg.get('third_party'):
        # 第三方用户不受密码策略约束
        lines.append(f"{n}. 确保第三方认证源（AD/RADIUS/Voucher等）中存在测试用户")
        n += 1
        lines.append(f"{n}. 调用模拟认证接口，使用第三方用户触发1x有线认证")
        n += 1
    else:
        login_type = cfg.get('login_type', '首次')
        if cfg.get('meets_policy'):
            pwd_desc = '符合密码策略的密码（如 Rui12345?，含大写+小写+数字+特殊字符）'
        else:
            pwd_desc = '不符合密码策略的密码（如 rui12345，不含大写字母和特殊字符）'
        lines.append(f"{n}. 调用用户管理接口，创建测试用户并设置{pwd_desc}")
        n += 1

        first = '首次' if login_type == '首次' else '非首次'
        lines.append(f"{n}. 调用模拟认证接口，触发用户{first}1x有线认证")
        n += 1

    # 5. 断言认证结果
    if '认证成功' in auth_result:
        lines.append(f"{n}. 调用认证日志查询接口，断言认证成功")
        n += 1
    elif '认证失败' in auth_result:
        failure_reason = auth_result.replace('认证失败-', '') if '-' in auth_result else ''
        lines.append(f"{n}. 调用认证日志查询接口，断言认证失败")
        n += 1
        if failure_reason:
            lines.append(f"{n}. 调用认证失败日志查询接口，断言失败原因包含「{failure_reason}」")
            n += 1
    else:
        lines.append(f"{n}. 调用认证日志查询接口，断言认证结果符合预期")
        n += 1

    # 6. 清理
    lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户/恢复密码策略默认配置")

    return "\n".join(lines)


def determine_directory(test_point, name):
    """确定用例目录分类"""
    if '展示' in test_point:
        return 'dot1x密码复杂度/密码安全管理页面-UI展示'
    elif '输入参数' in test_point:
        return 'dot1x密码复杂度/密码安全管理页面-参数校验'
    elif '802.1x密码校验短信通知' in test_point:
        return 'dot1x密码复杂度/短信通知配置-UI展示'
    elif '定时任务' in test_point:
        return 'dot1x密码复杂度/定时任务'
    elif '第三方用户' in test_point or '1x第三方' in test_point:
        return 'dot1x密码复杂度/认证组合-第三方用户'
    elif '首次用户登录' in test_point:
        return 'dot1x密码复杂度/认证组合-首次登录'
    elif '非首次用户登录' in test_point:
        return 'dot1x密码复杂度/认证组合-非首次登录'
    return 'dot1x密码复杂度/其他'


# ══════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════

def main():
    print("📖 读取飞书表格 UmATpA ...")
    cases = read_sheet()
    print(f"   读取到 {len(cases)} 条用例")

    print("🔍 分析用例...")
    results = []
    for i, case in enumerate(cases, start=1):
        cid = case.get('用例编号', f'TP-{i:03d}')
        test_point = case.get('测试点描述', '')
        name = case.get('用例名称', '') or ''
        desc = case.get('用例描述', '') or ''
        precondition = case.get('预置条件', '') or ''
        steps = case.get('测试步骤', '') or ''
        expect = case.get('期望结果', '') or ''

        automatable, no_auto_reason = classify_case(test_point, name, steps, expect)
        auto_steps = generate_automation_steps(test_point, name, precondition, steps, expect)
        script_name = generate_script_name(test_point, name, expect)
        directory = determine_directory(test_point, name)

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

    # 保存 JSON
    result_file = os.path.join(WORKSPACE, 'dot1x_passwd_analysis_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"   分析结果已保存: {result_file}")

    # 生成报告
    report = generate_report(results)
    report_file = os.path.join(WORKSPACE, 'dot1x_passwd_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 分析报告已生成: {report_file}")

    print("✅ 分析完成（回写请运行 write_dot1x_to_lark.py）")


def generate_report(results):
    """生成 Markdown 分析报告"""
    lines = []
    lines.append("# 802.1x密码复杂度用例自动化分析报告\n")
    lines.append("**分析日期**: 2026-03-05  ")
    lines.append(f"**用例总数**: {len(results)}  ")

    auto_yes = sum(1 for r in results if r['是否可自动化'] == '是')
    auto_no = sum(1 for r in results if r['是否可自动化'] == '否')
    lines.append(f"**可自动化**: {auto_yes} | **不可自动化**: {auto_no}\n")

    # 目录结构
    lines.append("---\n")
    lines.append("## 📁 建议目录结构\n")
    lines.append("```")
    dirs = {}
    for r in results:
        d = r['目录分类']
        dirs.setdefault(d, []).append(f"{r['用例编号']} {r['用例名称'][:60]}")
    for d in sorted(dirs.keys()):
        lines.append(f"{d}/")
        for c in dirs[d]:
            lines.append(f"    ├── {c}")
    lines.append("```\n")

    # 汇总表格
    lines.append("---\n")
    lines.append("## 📊 用例分析汇总\n")
    lines.append("| 编号 | 用例名称（摘要） | 可自动化 | 不可自动化原因 | 脚本名称 |")
    lines.append("|------|--------------|---------|--------------|---------|")
    for r in results:
        reason = r['不可自动化原因'][:40] if r['是否可自动化'] == '否' else ''
        name_short = r['用例名称'][:40]
        lines.append(f"| {r['用例编号']} | {name_short} | {r['是否可自动化']} | {reason} | {r['脚本名称'][:60]} |")
    lines.append("")

    # 详细分析
    lines.append("---\n")
    lines.append("## 📋 详细分析\n")
    for r in results:
        lines.append(f"### {r['用例编号']}\n")
        lines.append(f"**用例名称**: {r['用例名称']}  ")
        lines.append(f"**是否可自动化**: {r['是否可自动化']}  ")
        if r['不可自动化原因']:
            lines.append(f"**不可自动化原因**: {r['不可自动化原因']}  ")
        lines.append(f"**脚本名称**: `{r['脚本名称']}`  ")
        lines.append(f"**目录**: `{r['目录分类']}`\n")

        lines.append("**自动化关键步骤**:")
        lines.append("```")
        lines.append(r['自动化关键步骤'])
        lines.append("```\n")

        if r['期望结果']:
            lines.append("**期望结果**:")
            lines.append("```")
            lines.append(r['期望结果'])
            lines.append("```\n")

        lines.append("---\n")

    # 自动化建议
    lines.append("## 💡 自动化建议\n")
    lines.append("### 可自动化的用例\n")
    for r in results:
        if r['是否可自动化'] == '是':
            lines.append(f"- **{r['用例编号']}** {r['用例名称'][:60]}")
    lines.append("")

    lines.append("### 不可自动化的用例\n")
    for r in results:
        if r['是否可自动化'] == '否':
            lines.append(f"- **{r['用例编号']}** {r['用例名称'][:60]} — {r['不可自动化原因'][:50]}")
    lines.append("")

    lines.append("---\n")
    lines.append("**维护者**: 魏斌  ")
    lines.append("**生成时间**: 2026-03-05")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
