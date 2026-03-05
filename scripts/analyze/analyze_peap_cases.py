#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PEAP用例自动化分析脚本 v2
评审修订：
- 是否可自动化仅填 是/否，新增不可自动化原因列
- PEAP-060 纯页面检查→否
- 自动化关键步骤面向API拆解（接口调用+断言响应，合并"保存"到接口调用）
- 脚本名称从关键步骤中提炼，格式：场景-接口动作-断言结果
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

# ── 常量 ──────────────────────────────────────────────
LARK_APP_ID = "cli_a83faf50a228900e"
LARK_APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SHEET_URL = "https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=gBtCcn"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "gBtCcn"

REF_LOGIN_ADMIN = "引用51401"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')

# ══════════════════════════════════════════════════════
# 分类：只返回 是/否 + 不可自动化原因
# ══════════════════════════════════════════════════════

def classify_case(idx, name, steps, expect):
    """返回 (是否可自动化: '是'|'否', 不可自动化原因: str)"""
    name_lower = name.lower()

    # ── 需要物理设备 → 否 ──
    device_keywords = {
        'win11': 'Win11', 'macos': 'macOS', '小米手机': '小米手机',
        'oppo手机': 'OPPO手机', 'ios系统': 'iOS', 'ipad': 'iPad',
        'android pad': 'Android Pad', '鸿蒙系统': '鸿蒙系统'
    }
    for kw, label in device_keywords.items():
        if kw in name_lower:
            return '否', f'需要{label}物理设备进行真实802.1X无线认证，无法通过API模拟'

    # ── PEAP-060 纯页面检查 → 否 ──
    if idx == 60:
        return '否', '纯页面帮助说明文本检查，属于UI视觉验证，不适合API自动化'

    # ── 证书拖拽上传 → 否 ──
    if '证书上传方式' in name:
        return '否', '涉及拖拽上传等浏览器交互行为，需要UI自动化而非API自动化'

    # ── 其余均可通过API自动化 → 是 ──
    return '是', ''


# ══════════════════════════════════════════════════════
# 自动化关键步骤：面向API接口拆解
# ══════════════════════════════════════════════════════

def generate_automation_steps(idx, name, precondition, steps, expect):
    """生成面向API的自动化关键步骤"""
    lines = []
    n = 1

    # 1. 登录管理端
    lines.append(f"{n}. 登录管理端 - {REF_LOGIN_ADMIN}")
    n += 1

    # --- 证书文件限制 ---
    if '证书文件限制' in name:
        lines.append(f"{n}. 调用证书上传接口，传入非pfx/pem格式文件，断言接口返回文件格式错误")
        n += 1
        lines.append(f"{n}. 调用证书上传接口，传入>10MB文件，断言接口返回文件大小超出限制")
        n += 1
        lines.append(f"{n}. 调用证书上传接口，传入合法证书文件(<10MB)，断言上传成功")
        n += 1
        lines.append(f"{n}. 调用证书保存接口(含密码)，断言返回成功且包含重启提示信息")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 恢复原始证书配置")
        return "\n".join(lines)

    # --- 证书详情 ---
    if '证书详情' in name:
        lines.append(f"{n}. 调用证书上传接口，传入合法证书文件，断言上传成功")
        n += 1
        lines.append(f"{n}. 调用证书保存接口(含密码)，断言保存成功")
        n += 1
        lines.append(f"{n}. 调用证书详情查询接口，断言返回包含生效时间和到期时间字段")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 恢复原始证书配置")
        return "\n".join(lines)

    # --- 证书上传方式(拖拽) ---
    if '证书上传方式' in name:
        lines.append(f"{n}. 无法通过API自动化，需UI自动化覆盖拖拽上传交互")
        return "\n".join(lines)

    # --- 1x默认协议说明(纯UI) ---
    if '1x默认协议说明' in name:
        lines.append(f"{n}. 纯页面UI检查，不适合API自动化")
        return "\n".join(lines)

    # --- 1x认证默认协议选择 ---
    if '1x认证默认协议选择' in name:
        lines.append(f"{n}. 调用查询认证证书配置接口，断言默认1x认证协议为PEAP")
        n += 1
        lines.append(f"{n}. 调用修改1x认证默认协议接口，将协议设为EAP-TTLS，断言接口返回保存成功")
        n += 1
        lines.append(f"{n}. 调用修改1x认证默认协议接口，将协议设为空值，断言接口返回参数校验失败")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用修改接口恢复协议为PEAP")
        return "\n".join(lines)

    # --- 多平台兼容性 → 不可自动化 ---
    for kw in ['win11', 'macos', '小米手机', 'oppo手机', 'ios系统',
               'ipad', 'android pad', '鸿蒙系统']:
        if kw in name.lower():
            lines.append(f"{n}. 需要物理设备进行802.1X真实认证，无法通过API自动化")
            return "\n".join(lines)

    # ═══════ 核心认证流程用例 ═══════

    # 前置：配置认证源
    if precondition:
        if 'LDAP' in precondition or 'ldap' in precondition:
            lines.append(f"{n}. 调用认证源配置接口，创建/配置LDAP认证源及关联认证网络")
            n += 1
        if '1x认证默认协议' in precondition:
            protocol = 'PEAP' if 'PEAP' in precondition else 'EAP-TTLS'
            lines.append(f"{n}. 调用修改1x认证默认协议接口，设置为{protocol}，断言返回成功")
            n += 1

    # 前置：创建测试用户
    if '本地用户' in name or '本地账户' in name:
        lines.append(f"{n}. 调用用户管理接口，创建本地认证测试用户")
        n += 1
    elif '账号冲突' in name:
        lines.append(f"{n}. 调用用户管理接口，创建本地用户(与LDAP用户同名不同密码)")
        n += 1
        lines.append(f"{n}. 确保LDAP认证源中存在同名用户")
        n += 1
    elif 'LDAP' in name:
        lines.append(f"{n}. 确保LDAP认证源中存在测试用户")
        n += 1

    # 前置：LDAP密码存储/校验相关配置
    if '不加密' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置密码存储方式为明文(不加密)")
        n += 1
    elif 'MD4' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置密码加密方式为MD4")
        n += 1
    elif 'MD5 16' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置密码加密方式为MD5-16进制")
        n += 1
    elif 'MD5 Base64' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置密码加密方式为MD5-Base64")
        n += 1
    elif '加密存储' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置密码存储方式为加密存储")
        n += 1
    elif '不启用' in name and '校验' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置身份校验为不启用")
        n += 1
    elif '每次认证' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置身份校验频率为每次认证时")
        n += 1
    elif '定期' in name:
        lines.append(f"{n}. 调用LDAP认证源配置接口，设置身份校验频率为定期校验")
        n += 1

    # 核心步骤：解析测试步骤文本，转为API视角
    if steps:
        step_items = [re.sub(r'^\d+[\.\、]\s*', '', s.strip()) for s in steps.split('\n') if s.strip()]
        i = 0
        while i < len(step_items):
            item = step_items[i]

            # 「连接1x信号」→ 跳过（隐含在后续认证接口调用中）
            if '连接1x信号' in item or ('连接' in item and '信号' in item):
                # 看下一步是否是直接的认证动作（非认证源配置），合并
                if i + 1 < len(step_items) and '认证' in step_items[i + 1] and '认证源' not in step_items[i + 1]:
                    next_item = step_items[i + 1]
                    auth_desc = _parse_auth_action(next_item)
                    lines.append(f"{n}. 调用模拟认证接口，{auth_desc}")
                    n += 1
                    i += 2
                    continue
                else:
                    # 没有紧跟认证步骤，跳过连接步骤（后面的认证步骤会单独处理）
                    i += 1
                    continue

            # 「认证源使用默认配置」→ 配置步骤
            if '认证源' in item and '默认' in item:
                lines.append(f"{n}. 调用认证源配置接口，确保认证源为默认配置")
                n += 1
                i += 1
                continue

            # 「使用xx认证」单独出现
            if ('认证' in item and ('用户' in item or '进行' in item)) and '连接' not in item:
                auth_desc = _parse_auth_action(item)
                lines.append(f"{n}. 调用模拟认证接口，{auth_desc}")
                n += 1
                i += 1
                continue

            # 「查看管理端在线用户」→ 调用查询接口断言
            if '查看' in item and '在线' in item:
                step_num_str = str(i + 1)
                expect_text = _find_expect_for_step(step_num_str, expect)
                if '离线' in expect_text or '不在' in expect_text:
                    lines.append(f"{n}. 调用在线用户查询接口，断言用户和终端为离线状态")
                elif '在线' in expect_text:
                    lines.append(f"{n}. 调用在线用户查询接口，断言用户和终端为在线状态且信息正确")
                else:
                    lines.append(f"{n}. 调用在线用户查询接口，断言用户状态符合预期")
                n += 1
                i += 1
                continue

            # 「终端断开信号」
            if '断开' in item and '信号' in item:
                lines.append(f"{n}. 调用模拟断开接口（或仿真工具断开认证连接）")
                n += 1
                i += 1
                continue

            # 「管理端下线」
            if '管理端' in item and '下线' in item:
                lines.append(f"{n}. 调用管理端强制下线接口，下线目标终端")
                n += 1
                i += 1
                continue

            # 「自助端下线」
            if '自助' in item and '下线' in item:
                lines.append(f"{n}. 调用自助端下线接口，下线目标终端")
                n += 1
                i += 1
                continue

            # 「查看终端/用户信息」
            if '查看' in item and ('终端' in item or '用户信息' in item):
                lines.append(f"{n}. 调用终端/用户信息查询接口，断言终端信息和用户信息正确")
                n += 1
                i += 1
                continue

            # 「修改密码」
            if '修改' in item and '密码' in item:
                lines.append(f"{n}. 调用自助端修改密码接口，修改用户密码")
                n += 1
                i += 1
                continue

            # 「上传证书」
            if '上传' in item and '证书' in item:
                lines.append(f"{n}. 调用证书上传接口，传入证书文件")
                n += 1
                i += 1
                continue

            # 「点击保存」→ 跳过（合并到前面的接口调用）
            if '保存' in item and ('点击' in item or '确认' in item):
                i += 1
                continue

            # 「查看证书详情」
            if '证书详情' in item:
                lines.append(f"{n}. 调用证书详情查询接口，断言返回生效时间和到期时间")
                n += 1
                i += 1
                continue

            # 默认：保留原文
            lines.append(f"{n}. {item}")
            n += 1
            i += 1

    # 补充未覆盖的断言
    if expect and '认证失败' in expect and not any('失败' in l for l in lines[1:]):
        lines.append(f"{n}. 断言认证接口返回认证失败")
        n += 1

    # 清理
    lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户/恢复认证配置")
    return "\n".join(lines)


def _parse_auth_action(text):
    """从认证描述中提取API动作"""
    if '错误密码' in text or '错误' in text:
        return '使用错误密码，断言认证接口返回认证失败'
    if '不存在' in text:
        return '使用不存在的账号，断言认证接口返回用户不存在'
    if 'LDAP账户的密码' in text:
        return '使用LDAP用户(LDAP密码)认证'
    if '本地账户的密码' in text:
        return '使用LDAP用户(本地密码)认证'
    if 'LDAP' in text:
        return '使用LDAP用户认证'
    if '新密码' in text:
        return '使用修改后的新密码认证'
    if '本地' in text:
        return '使用本地用户认证'
    return '触发用户认证'


def _find_expect_for_step(step_num, expect):
    """从预期结果中找到对应步骤编号的期望"""
    if not expect:
        return ''
    for line in expect.split('\n'):
        line = line.strip()
        if line.startswith(f"{step_num}.") or line.startswith(f"{step_num}、"):
            return line
    return ''


# ══════════════════════════════════════════════════════
# 脚本名称：从关键步骤中提炼，拼接 场景-接口动作-断言结果
# ══════════════════════════════════════════════════════

def generate_script_name(idx, name, auto_steps, expect):
    """从自动化关键步骤中提炼脚本名称"""

    # --- 特殊用例直接指定 ---
    if '1x认证默认协议选择' in name:
        return '协议切换-调用修改1x认证默认协议接口切换EAP-TTLS并校验空值-断言保存成功和参数校验失败'

    if '1x默认协议说明' in name:
        return '不可自动化-纯页面帮助说明文本检查'

    if '证书文件限制' in name:
        return '证书上传-调用上传接口校验格式和大小限制-断言非法文件报错合法文件成功'

    if '证书上传方式' in name:
        return '不可自动化-证书拖拽上传需UI自动化'

    if '证书详情' in name:
        return '证书详情-调用上传保存接口后查询详情-断言返回生效时间和到期时间'

    # --- 多平台兼容性 ---
    platform_map = {
        'win11': 'Win11', 'macos': 'macOS', '小米手机': '小米',
        'oppo手机': 'OPPO', 'ios系统': 'iOS', 'ipad': 'iPad',
        'android pad': 'AndroidPad', '鸿蒙系统': '鸿蒙'
    }
    for kw, label in platform_map.items():
        if kw in name.lower():
            protocol = 'PEAP' if 'PEAP' in name else 'EAP-TTLS'
            return f'不可自动化-{label}使用{protocol}认证需物理设备'

    # --- 认证流程用例：场景-动作-断言 ---
    parts = []

    # 协议
    if 'PEAP' in name:
        parts.append('PEAP')
    elif 'EAP-TTLS' in name:
        parts.append('EAP-TTLS')

    # 用户类型 + 特殊场景
    if '不对接LDAP' in name and '本地账户' in name:
        parts.append('无LDAP源本地用户')
    elif '不对接LDAP' in name and 'LDAP' in name:
        parts.append('无LDAP源LDAP用户')
    elif '账号冲突' in name:
        parts.append('本地LDAP同名用户冲突')
    elif '密码错误' in name:
        parts.append('LDAP用户错误密码')
    elif '账号不存在' in name:
        parts.append('不存在账号')
    elif '自助功能' in name:
        parts.append('LDAP用户自助功能')
    elif '本地用户' in name or '本地账户' in name:
        parts.append('本地用户')
    elif '登录LDAP服务器' in name and '身份校验' in name:
        parts.append('LDAP登录校验方式')
    elif '查询LDAP用户信息' in name and '身份校验' in name:
        parts.append('LDAP查询校验方式')
    elif '认证校验密码' in name:
        parts.append('LDAP认证校验密码')
    elif 'LDAP' in name:
        parts.append('LDAP用户')

    # 接口动作
    if '主动下线' in name:
        parts.append('触发认证后模拟终端断开')
    elif '自助端下线' in name:
        parts.append('触发认证后调用自助端下线接口')
    elif '管理端下线' in name:
        parts.append('触发认证后调用管理端强制下线接口')
    elif '自助功能' in name:
        parts.append('触发认证-查询信息-修改密码-自助下线-新密码重认证')
    elif '不加密' in name:
        parts.append('配置明文存储后触发认证')
    elif 'MD4' in name:
        parts.append('配置MD4加密后触发认证')
    elif 'MD5 16' in name:
        parts.append('配置MD5-Hex加密后触发认证')
    elif 'MD5 Base64' in name:
        parts.append('配置MD5-Base64加密后触发认证')
    elif '加密存储' in name:
        parts.append('配置加密存储后触发认证')
    elif '不启用' in name:
        parts.append('配置不校验密码后触发认证')
    elif '每次认证' in name:
        parts.append('配置每次到LDAP校验后触发认证')
    elif '定期' in name:
        parts.append('配置定期到LDAP校验后触发认证')
    elif '密码错误' in name:
        parts.append('触发认证使用错误密码')
    elif '账号不存在' in name:
        parts.append('触发认证使用不存在账号')
    elif '账号冲突' in name:
        parts.append('分别用LDAP密码和本地密码认证')
    elif '不对接LDAP' in name:
        parts.append('触发认证')
    else:
        parts.append('触发认证')

    # 断言结果
    if expect:
        if '认证失败' in expect and '认证成功' in expect:
            parts.append('断言LDAP密码失败本地密码成功')
        elif '认证失败' in expect:
            parts.append('断言认证失败')
        elif '在线' in expect and '离线' in expect:
            parts.append('断言查询接口返回在线后离线')
        elif '认证成功' in expect:
            parts.append('断言认证成功且查询在线正确')

    return '-'.join(parts)


def determine_directory(name):
    """根据用例名称确定所属目录分类"""
    if any(kw in name.lower() for kw in ['win11', 'macos', '小米手机', 'oppo手机',
                                          'ios系统', 'ipad', 'android pad', '鸿蒙系统']):
        return 'PEAP认证/多平台兼容性'
    if '证书' in name:
        return 'PEAP认证/证书管理'
    if '1x' in name.lower():
        return 'PEAP认证/协议配置'

    prefix = 'PEAP认证/PEAP协议' if 'PEAP' in name else 'PEAP认证/EAP-TTLS协议'

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


# ══════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════

def main():
    print("📖 读取飞书表格...")
    reader = LarkSheetReader(LARK_APP_ID, LARK_APP_SECRET)
    cases = reader.read_from_url(SHEET_URL)
    print(f"   读取到 {len(cases)} 条用例")

    print("🔍 分析用例...")
    analysis_results = []
    for i, case in enumerate(cases, start=1):
        case_id = f"PEAP-{i:03d}"
        name = case.get('用例名称', '') or ''
        desc = case.get('用例描述', '') or ''
        precondition = case.get('预置条件', '') or ''
        steps = case.get('测试步骤', '') or ''
        expect = case.get('期望结果', '') or ''

        automatable, no_auto_reason = classify_case(i, name, steps, expect)
        auto_steps = generate_automation_steps(i, name, precondition, steps, expect)
        script_name = generate_script_name(i, name, auto_steps, expect)
        directory = determine_directory(name)

        analysis_results.append({
            '用例编号': case_id,
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
    result_file = os.path.join(WORKSPACE, 'peap_analysis_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    print(f"   分析结果已保存: {result_file}")

    # 生成报告
    report = generate_report(analysis_results)
    report_file = os.path.join(WORKSPACE, 'peap_automation_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 分析报告已生成: {report_file}")

    print("✅ 分析完成（回写请运行 write_peap_to_lark.py）")


def generate_report(results):
    """生成 Markdown 分析报告"""
    lines = []
    lines.append("# PEAP认证用例自动化分析报告\n")
    lines.append("**分析日期**: 2026-03-05  ")
    lines.append(f"**用例总数**: {len(results)}  ")

    auto_yes = sum(1 for r in results if r['是否可自动化'] == '是')
    auto_no = sum(1 for r in results if r['是否可自动化'] == '否')
    lines.append(f"**可自动化**: {auto_yes} | **不可自动化**: {auto_no}\n")

    # ── 目录结构 ──
    lines.append("---\n")
    lines.append("## 📁 建议目录结构\n")
    lines.append("```")
    dirs = {}
    for r in results:
        d = r['目录分类']
        dirs.setdefault(d, []).append(f"{r['用例编号']} {r['用例名称']}")
    for d in sorted(dirs.keys()):
        lines.append(f"{d}/")
        for case in dirs[d]:
            lines.append(f"    ├── {case}")
    lines.append("```\n")

    # ── 汇总表格 ──
    lines.append("---\n")
    lines.append("## 📊 用例分析汇总\n")
    lines.append("| 编号 | 用例名称 | 可自动化 | 不可自动化原因 | 脚本名称 |")
    lines.append("|------|---------|---------|--------------|---------|")
    for r in results:
        reason = r['不可自动化原因'] if r['是否可自动化'] == '否' else ''
        lines.append(f"| {r['用例编号']} | {r['用例名称']} | {r['是否可自动化']} | {reason} | {r['脚本名称']} |")
    lines.append("")

    # ── 详细分析 ──
    lines.append("---\n")
    lines.append("## 📋 详细分析\n")
    for r in results:
        lines.append(f"### {r['用例编号']} {r['用例名称']}\n")
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

    # ── 分类建议 ──
    lines.append("## 💡 自动化建议\n")
    lines.append("### 可自动化的用例")
    lines.append("以下用例可通过管理端API + 模拟认证接口完成自动化：\n")
    for r in results:
        if r['是否可自动化'] == '是':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']}")
    lines.append("")

    lines.append("### 不可自动化的用例\n")
    for r in results:
        if r['是否可自动化'] == '否':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']} — {r['不可自动化原因']}")
    lines.append("")

    lines.append("---\n")
    lines.append("**维护者**: 魏斌  ")
    lines.append("**生成时间**: 2026-03-05")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
