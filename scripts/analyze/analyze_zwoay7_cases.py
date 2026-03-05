#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
linkage消息通告优化用例自动化分析脚本
读取飞书表格 ZwoaY7 → 分析自动化可行性 → 生成脚本名称/自动化步骤 → 输出结果

现有列: A=测试点 B=用例标签 C=用例编号 D=用例名称 E=用例描述
        F=预置条件 G=测试步骤 H=期望结果
新增列: J=是否可自动化 K=不可自动化原因 L=脚本名称

不可自动化原因：
  测试验证步骤依赖 docker 命令行进入容器查看 linkage 日志，
  以及 Another Redis Desktop Manager 桌面 GUI 工具检查 Redis
  事件存储，无法通过自动化接口实现。
"""

import sys
import os
import json
import requests

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'skills', 'lark-skills', 'lark-sheet-reader'))

from lark_sheet_reader import LarkSheetReader

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
SPREADSHEET_TOKEN = "Mw7escaVhh92SSts8incmbbUnkc"
SHEET_ID = "ZwoaY7"
BASE_URL = "https://open.feishu.cn/open-apis"
REF_LOGIN_ADMIN = "引用51401"
WORKSPACE = os.path.join(project_root, 'sandbox', 'workspace')

# 不可自动化的用例编号集合
# 测试步骤依赖 docker exec / docker logs 进入容器查看 linkage 日志
# 以及以及 Another Redis Desktop Manager GUI 工具验证 Redis 事件存储
_NO_AUTO_IDS = {
    'linkage-YW-001', 'linkage-YW-002', 'linkage-YW-003', 'linkage-YW-004',
    'linkage-YW-006', 'linkage-YW-007', 'linkage-YW-008', 'linkage-YW-009',
    'linkage-YW-011', 'linkage-YW-012', 'linkage-YW-013', 'linkage-YW-014',
    'linkage-YW-016', 'linkage-YW-017',
    'linkage-YW-021',
    'linkage-YW-046', 'linkage-YW-047', 'linkage-YW-048',
}

_REASON_DOCKER_REDIS = (
    "测试验证步骤依赖docker命令行(docker ps/docker logs)进入容器查看linkage日志，"
    "以及Another Redis Desktop Manager桌面GUI工具检查Redis事件存储，无法通过自动化接口实现"
)
_REASON_KAFKA_REDIS = (
    "验证步骤需确认linkage未转发kafka消息且未写入Redis，"
    "依赖Redis桌面工具和docker容器日志验证，无法通过API接口完成"
)


# ══════════════════════════════════════════════════════
# 读取飞书表格
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
    url = BASE_URL + '/sheets/v2/spreadsheets/' + SPREADSHEET_TOKEN + '/values/' + SHEET_ID + '!A1:P400'
    rows = requests.get(url, headers=hdrs).json().get('data', {}).get('valueRange', {}).get('values', [])

    col_names = [cell_text(h) for h in rows[0]]
    col_names[0] = '测试点'

    cases = []
    for row in rows[1:]:
        if not any(cell_text(c) for c in row):
            continue
        d = {col_names[i]: cell_text(row[i]) if i < len(row) else '' for i in range(len(col_names))}
        if d.get('用例编号', ''):
            cases.append(d)
    return cases


# ══════════════════════════════════════════════════════
# 分类
# ══════════════════════════════════════════════════════

def classify_case(case_id, name, steps, expect):
    if case_id in _NO_AUTO_IDS:
        if '021' in case_id:
            return '否', _REASON_KAFKA_REDIS
        return '否', _REASON_DOCKER_REDIS
    return '是', ''


# ══════════════════════════════════════════════════════
# 自动化关键步骤
# ══════════════════════════════════════════════════════

def generate_automation_steps(case_id, name, precondition, steps, expect):
    if case_id in _NO_AUTO_IDS:
        return ''

    num_str = case_id.split('-')[-1]
    num = int(num_str) if num_str.isdigit() else 0

    lines = []
    n = 1

    lines.append(f"{n}. 登录管理端 - {REF_LOGIN_ADMIN}")
    n += 1

    # ── 005/010/015: UNC查看认证上下线消息 ──
    if num in (5, 10, 15):
        auth_map = {5: '1X', 10: 'portal', 15: '无感'}
        auth = auth_map[num]
        lines.append(f"{n}. 调用模拟{auth}认证接口，触发测试用户上线，记录触发次数")
        n += 1
        lines.append(f"{n}. 调用UNC策略随行-业务随身行-安全组-终端认证在线列表查询接口，"
                     f"断言上线事件次数与终端实际上线次数一致")
        n += 1
        lines.append(f"{n}. 调用强制下线接口，使测试用户下线，记录下线次数")
        n += 1
        lines.append(f"{n}. 再次调用终端认证在线列表查询接口，断言下线事件次数与终端实际下线次数一致")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    # ── 018-020: 有线认证类 ──
    if num in (18, 19, 20):
        auth_map = {18: 'portal', 19: '1x', 20: '无感'}
        auth = auth_map[num]
        lines.append(f"{n}. 完成有线{auth}认证所需前置配置（认证模板/用户/策略），调用相关管理接口")
        n += 1
        lines.append(f"{n}. 调用模拟有线{auth}认证接口，触发测试用户上线")
        n += 1
        lines.append(f"{n}. 调用策略随行-终端认证在线列表查询接口，断言用户在线记录存在")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户/策略配置")
        return "\n".join(lines)

    # ── 022-033: 各类 portal 扩展认证 ──
    auth_name_map = {
        22: '钉钉扫码', 23: '飞书扫码', 24: '飞书内免认证', 25: '短信验证码',
        26: '扫码', 27: '访客授权码', 28: '访客短信', 29: '访客一键上网',
        30: '微信入网', 31: '企业微信扫码', 32: 'web认证后短信二次认证', 33: '计费copy',
    }
    if num in auth_name_map:
        auth = auth_name_map[num]
        lines.append(f"{n}. 调用认证配置接口，完成{auth}认证所需前置配置")
        n += 1
        lines.append(f"{n}. 调用模拟{auth}认证接口，触发测试用户上线")
        n += 1
        lines.append(f"{n}. 调用策略随行-终端认证在线列表查询接口，断言用户在线记录存在")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    # ── 034: 用户名强制下线（用户名抢占） ──
    if num == 34:
        lines.append(f"{n}. 调用用户管理接口，创建测试用户，配置同一用户名只允许一个终端在线")
        n += 1
        lines.append(f"{n}. 调用模拟认证接口，使用测试用户在终端A上线，调用在线用户查询接口断言终端A在线")
        n += 1
        lines.append(f"{n}. 调用模拟认证接口，使用相同用户名在终端B发起认证（触发用户名抢占强制下线终端A）")
        n += 1
        lines.append(f"{n}. 调用在线用户查询接口，断言终端A不在线、终端B在线（用户名抢占成功）")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户")
        return "\n".join(lines)

    # ── 035-045: 各类开户 ──
    open_acct_map = {
        35: ('单个开户', '调用用户管理-新增用户接口，创建单个用户'),
        36: ('批量开户', '调用用户管理-批量新增用户接口，一次性创建多个用户'),
        37: ('导入开户', '调用用户管理-导入用户接口，上传用户CSV/Excel文件批量创建用户'),
        38: ('LDAP认证开户', '配置LDAP服务器，LDAP用户首次认证时触发自动开户，调用用户查询接口断言用户已创建'),
        39: ('LDAP登录自助开户', '配置LDAP服务器自助端，LDAP用户登录自助端时触发自动开户，调用用户查询接口断言用户已创建'),
        40: ('LDAP手动同步开户', '调用LDAP手动同步接口，批量同步LDAP用户到本地用户库，调用用户查询接口断言同步成功'),
        41: ('AD认证开户', '配置AD域服务器，AD用户首次认证时触发自动开户，调用用户查询接口断言用户已创建'),
        42: ('对接radius认证开户', '配置对接Radius服务器，Radius用户认证时触发自动开户，调用用户查询接口断言用户已创建'),
        43: ('Vouchers开户', '调用Vouchers管理接口，创建Vouchers码，使用Vouchers码发起认证触发开户，调用用户查询接口断言用户已创建'),
        44: ('Eupsk开户', '调用Eupsk管理接口，创建Eupsk用户，发起Eupsk认证触发开户，调用用户查询接口断言用户已创建'),
        45: ('访客短信开户', '调用访客管理接口，通过短信验证码方式注册访客用户，调用用户查询接口断言访客用户已创建'),
    }
    if num in open_acct_map:
        label, detail = open_acct_map[num]
        lines.append(f"{n}. {detail}")
        n += 1
        lines.append(f"{n}. 调用策略随行-全部用户列表查询接口，断言新开户用户已同步出现在列表中")
        n += 1
        lines.append(f"{n}. 清理测试数据 - 调用接口删除测试用户")
        return "\n".join(lines)

    # ── 049: 销户用户 ──
    if num == 49:
        lines.append(f"{n}. 调用用户管理接口，确认目标测试用户存在")
        n += 1
        lines.append(f"{n}. 调用用户管理-删除用户接口，执行销户操作")
        n += 1
        lines.append(f"{n}. 调用模拟认证接口，使用已销户用户名发起认证")
        n += 1
        lines.append(f"{n}. 调用认证日志或在线用户查询接口，断言销户后认证失败/用户已不存在")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    # ── 050: 自动预销户 ──
    if num == 50:
        lines.append(f"{n}. 调用用户管理接口，查询并确认目标用户状态")
        n += 1
        lines.append(f"{n}. 调用用户管理接口，配置用户自动预销户条件（如设置账户有效期/到期策略）")
        n += 1
        lines.append(f"{n}. 调用策略随行-用户列表查询接口，断言满足条件的用户状态已变为预销户")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    # ── 051: 批量上下线压测 ──
    if num == 51:
        lines.append(f"{n}. 调用批量模拟认证接口或性能测试工具，批量触发大量用户上线，记录实际上线次数")
        n += 1
        lines.append(f"{n}. 调用策略随行-终端认证在线列表查询接口，断言在线记录数量与实际上线次数一致")
        n += 1
        lines.append(f"{n}. 调用批量下线接口，批量触发用户下线")
        n += 1
        lines.append(f"{n}. 再次调用在线列表查询接口，断言上下线事件次数记录准确")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    # ── 052: 证书认证 ──
    if num == 52:
        lines.append(f"{n}. 调用证书管理配置接口，完成证书认证前置配置（导入证书/配置认证模板）")
        n += 1
        lines.append(f"{n}. 调用模拟证书认证接口，触发证书认证用户上线")
        n += 1
        lines.append(f"{n}. 调用策略随行-终端认证在线列表查询接口，断言用户在线记录存在")
        n += 1
        lines.append(f"{n}. 调用强制下线接口，触发证书认证用户下线")
        n += 1
        lines.append(f"{n}. 调用策略随行在线列表查询接口，断言用户下线；调用用户管理认证历史接口，断言上下线记录完整")
        n += 1
        lines.append(f"{n}. 清理测试数据")
        return "\n".join(lines)

    return ''


# ══════════════════════════════════════════════════════
# 脚本名称
# ══════════════════════════════════════════════════════

def generate_script_name(case_id, name, automatable):
    if automatable == '否':
        return ''

    num_str = case_id.split('-')[-1]
    num = int(num_str) if num_str.isdigit() else 0

    if num == 5:
        return '1X认证上下线消息-调用UNC终端认证在线列表查询接口-断言上下线事件次数与实际一致'
    if num == 10:
        return 'portal认证上下线消息-调用UNC终端认证在线列表查询接口-断言上下线事件次数与实际一致'
    if num == 15:
        return '无感认证上下线消息-调用UNC终端认证在线列表查询接口-断言上下线事件次数与实际一致'
    if num == 18:
        return '有线portal认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 19:
        return '有线1x认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 20:
        return '有线无感认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 22:
        return '钉钉扫码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 23:
        return '飞书扫码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 24:
        return '飞书内免认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 25:
        return '短信验证码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 26:
        return '扫码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 27:
        return '访客授权码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 28:
        return '访客短信认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 29:
        return '访客一键上网认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 30:
        return '微信入网认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 31:
        return '企业微信扫码认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 32:
        return 'web认证后短信二次认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 33:
        return '计费copy认证-触发认证-调用策略随行在线列表接口-断言用户在线记录存在'
    if num == 34:
        return '用户名强制下线-调用强制下线接口触发用户名抢占-断言原终端下线新终端上线'
    if num == 35:
        return '单个开户-调用用户管理新增接口创建用户-调用策略随行用户列表接口断言用户同步成功'
    if num == 36:
        return '批量开户-调用用户管理批量新增接口-调用策略随行用户列表接口断言用户同步成功'
    if num == 37:
        return '导入开户-调用用户管理导入接口批量创建用户-调用策略随行用户列表接口断言同步成功'
    if num == 38:
        return 'LDAP认证开户-LDAP用户首次认证触发自动开户-调用策略随行用户列表接口断言用户已创建'
    if num == 39:
        return 'LDAP自助端开户-LDAP用户登录自助端触发开户-调用策略随行用户列表接口断言用户已创建'
    if num == 40:
        return 'LDAP手动同步开户-调用手动同步接口批量导入LDAP用户-调用策略随行用户列表接口断言同步成功'
    if num == 41:
        return 'AD认证开户-AD用户首次认证触发自动开户-调用策略随行用户列表接口断言用户已创建'
    if num == 42:
        return 'Radius认证开户-Radius用户认证触发自动开户-调用策略随行用户列表接口断言用户已创建'
    if num == 43:
        return 'Vouchers开户-创建Vouchers码触发认证开户-调用策略随行用户列表接口断言用户已创建'
    if num == 44:
        return 'Eupsk开户-Eupsk认证触发开户-调用策略随行用户列表接口断言用户已创建'
    if num == 45:
        return '访客短信开户-短信验证码注册访客用户-调用策略随行用户列表接口断言访客用户已创建'
    if num == 49:
        return '销户用户-调用删除用户接口执行销户-调用模拟认证接口断言销户后认证失败'
    if num == 50:
        return '自动预销户用户-调用用户管理接口配置预销户条件-调用策略随行用户列表接口断言用户预销户状态'
    if num == 51:
        return '用户批量上下线-调用批量认证接口大量用户上下线-调用在线列表接口断言事件记录准确'
    if num == 52:
        return '证书认证上下线-触发证书认证及下线-调用策略随行在线列表和用户管理接口断言记录完整'
    return name[:60]


def determine_directory(case_id, name):
    num_str = case_id.split('-')[-1]
    num = int(num_str) if num_str.isdigit() else 0
    if num in (1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 46, 47, 48):
        return 'linkage消息通告/不可自动化(依赖docker日志+RedisGUI)'
    if num in (5, 10, 15):
        return 'linkage消息通告/UNC上下线事件查询'
    if num in (18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33):
        return 'linkage消息通告/认证在线列表验证'
    if num == 34:
        return 'linkage消息通告/用户名强制下线'
    if num in range(35, 46):
        return 'linkage消息通告/开户场景'
    if num in (49, 50):
        return 'linkage消息通告/销户场景'
    if num in (51, 52):
        return 'linkage消息通告/特殊场景'
    return 'linkage消息通告/其他'


# ══════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════

def main():
    print("📖 读取飞书表格 ZwoaY7 ...")
    cases = read_sheet()
    print(f"   读取到 {len(cases)} 条用例")

    print("🔍 分析用例...")
    results = []
    for case in cases:
        cid = case.get('用例编号', '')
        name = case.get('用例名称', '') or ''
        test_point = case.get('测试点', '') or ''
        precondition = case.get('预置条件', '') or ''
        steps = case.get('测试步骤', '') or ''
        expect = case.get('期望结果', '') or ''
        desc = case.get('用例描述', '') or ''

        automatable, reason = classify_case(cid, name, steps, expect)
        auto_steps = generate_automation_steps(cid, name, precondition, steps, expect)
        script_name = generate_script_name(cid, name, automatable)
        directory = determine_directory(cid, name)

        results.append({
            '用例编号': cid,
            '测试点': test_point,
            '用例名称': name,
            '用例描述': desc,
            '预置条件': precondition,
            '测试步骤': steps,
            '期望结果': expect,
            '是否可自动化': automatable,
            '不可自动化原因': reason,
            '自动化关键步骤': auto_steps,
            '脚本名称': script_name,
            '目录分类': directory,
        })

    result_file = os.path.join(WORKSPACE, 'zwoay7_analysis_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"   分析结果已保存: {result_file}")

    report = generate_report(results)
    report_file = os.path.join(WORKSPACE, 'zwoay7_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 分析报告已生成: {report_file}")
    print("✅ 分析完成（回写请运行 write_zwoay7_to_lark.py）")


def generate_report(results):
    lines = []
    lines.append("# linkage消息通告优化用例自动化分析报告\n")
    lines.append("**分析日期**: 2026-03-05  ")
    lines.append(f"**用例总数**: {len(results)}  ")
    auto_yes = sum(1 for r in results if r['是否可自动化'] == '是')
    auto_no = sum(1 for r in results if r['是否可自动化'] == '否')
    lines.append(f"**可自动化**: {auto_yes} | **不可自动化**: {auto_no}\n")

    lines.append("---\n")
    lines.append("## ⚠️ 不可自动化原因说明\n")
    lines.append("以下 18 条用例的测试验证步骤包含：")
    lines.append("1. `docker ps` / `docker logs -f {容器名称}` 进入容器查看 linkage 服务日志")
    lines.append("2. **Another Redis Desktop Manager** 桌面 GUI 工具，人工核查 Redis 中的事件存储")
    lines.append("\n上述步骤无法通过 HTTP API 接口自动化实现，需要测试人员手动执行。\n")

    lines.append("---\n")
    lines.append("## 📁 建议目录结构\n```")
    dirs = {}
    for r in results:
        dirs.setdefault(r['目录分类'], []).append(f"{r['用例编号']} {r['用例名称'][:50]}")
    for d in sorted(dirs):
        lines.append(f"{d}/")
        for c in dirs[d]:
            lines.append(f"    ├── {c}")
    lines.append("```\n")

    lines.append("---\n")
    lines.append("## 📊 用例分析汇总\n")
    lines.append("| 编号 | 用例名称 | 可自动化 | 脚本名称/不可自动化原因 |")
    lines.append("|------|---------|---------|----------------------|")
    for r in results:
        if r['是否可自动化'] == '是':
            detail = r['脚本名称'][:80]
        else:
            detail = r['不可自动化原因'][:60] + '...'
        lines.append(f"| {r['用例编号']} | {r['用例名称'][:40]} | {r['是否可自动化']} | {detail} |")
    lines.append("")

    lines.append("---\n")
    lines.append("## 📋 详细分析\n")
    for r in results:
        lines.append(f"### {r['用例编号']} {r['用例名称']}\n")
        lines.append(f"**是否可自动化**: {r['是否可自动化']}  ")
        if r['不可自动化原因']:
            lines.append(f"**不可自动化原因**: {r['不可自动化原因']}  ")
        if r['脚本名称']:
            lines.append(f"**脚本名称**: `{r['脚本名称']}`  ")
        lines.append(f"**目录**: `{r['目录分类']}`\n")
        if r['自动化关键步骤']:
            lines.append("**自动化关键步骤**:\n```")
            lines.append(r['自动化关键步骤'])
            lines.append("```\n")
        lines.append("---\n")

    lines.append("## 💡 可自动化用例列表\n")
    for r in results:
        if r['是否可自动化'] == '是':
            lines.append(f"- **{r['用例编号']}** {r['用例名称']}")
    lines.append("\n---\n")
    lines.append("**维护者**: 魏斌  ")
    lines.append("**生成时间**: 2026-03-05")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
