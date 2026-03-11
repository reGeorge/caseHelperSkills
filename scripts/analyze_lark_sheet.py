#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从飞书表格拉取手工用例，运行 case-design-analyzer v2，输出自动化可行性报告
用法: python scripts/analyze_lark_sheet.py <飞书URL>
"""

import sys
import json
import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'lark-skills', 'lark-sheet-reader'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'case-skills', 'case-design-analyzer'))

from lark_sheet_reader import LarkSheetReader
from case_design_analyzer import ManualCase, CaseDesignAnalyzer

APP_ID = "cli_a83faf50a228900e"
APP_SECRET = "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"

COLUMN_MAP = {
    "case_id":        ["用例编号", "编号", "ID", "id"],
    "case_title":     ["用例名称", "用例标题", "标题", "名称"],
    "precondition":   ["预置条件", "前置条件", "前提条件"],
    "steps":          ["测试步骤", "操作步骤", "步骤"],
    "expected_result":["期望结果", "预期结果", "期望"],
}

AUTO_COL = ["是否可自动化", "可自动化", "是否支持自动化"]


def find_col(row: dict, candidates: list) -> str:
    for c in candidates:
        if c in row:
            return str(row[c] or "").strip()
    return ""


def parse_steps(text: str) -> list:
    if not text or text == "None":
        return [{"step_id": 1, "description": "（无步骤）"}]
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    steps = []
    for i, line in enumerate(lines, 1):
        desc = re.sub(r'^[\d]+[\.、．\)\s]\s*', '', line)
        steps.append({"step_id": i, "description": desc or line})
    return steps


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else \
        "https://ruijie.feishu.cn/sheets/Mw7escaVhh92SSts8incmbbUnkc?sheet=gBtCcn"

    print(f"🔗 URL: {url}")

    # ── Step 1: 读取飞书数据 ──────────────────────────────────────────────
    print("\n📥 读取飞书表格...")
    reader = LarkSheetReader(APP_ID, APP_SECRET)
    raw = reader.read_from_url(url)
    print(f"   原始行数: {len(raw)}")

    if not raw:
        print("❌ 表格为空，退出")
        sys.exit(1)

    print(f"   列字段: {list(raw[0].keys())}")

    # ── Step 2: 转换格式 ──────────────────────────────────────────────────
    cases = []
    skipped = 0
    auto_yes, auto_no = [], []

    for row in raw:
        cid = find_col(row, COLUMN_MAP["case_id"])
        if not cid:
            skipped += 1
            continue

        title = find_col(row, COLUMN_MAP["case_title"])
        precondition = find_col(row, COLUMN_MAP["precondition"])
        steps_text = find_col(row, COLUMN_MAP["steps"])
        expected = find_col(row, COLUMN_MAP["expected_result"])

        # 记录自动化标记
        auto_flag = find_col(row, AUTO_COL)

        case = ManualCase(
            case_id=cid,
            case_title=title,
            precondition=precondition,
            steps=parse_steps(steps_text),
            expected_result=expected,
        )
        cases.append(case)

        if "是" in auto_flag or "yes" in auto_flag.lower():
            auto_yes.append(cid)
        elif auto_flag:
            auto_no.append(cid)

    print(f"   有效用例: {len(cases)} 条 (跳过空行: {skipped})")
    print(f"   人工标注 可自动化: {len(auto_yes)} | 不可自动化: {len(auto_no)}")

    # ── Step 3: 保存转换后 JSON ───────────────────────────────────────────
    os.makedirs(os.path.join(PROJECT_ROOT, "workspace", "analysis"), exist_ok=True)
    raw_json_path = os.path.join(PROJECT_ROOT, "workspace", "analysis", "lark_peap_cases.json")
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump([{
            "case_id": c.case_id,
            "case_title": c.case_title,
            "precondition": c.precondition,
            "steps": c.steps,
            "expected_result": c.expected_result,
        } for c in cases], f, ensure_ascii=False, indent=2)
    print(f"\n💾 原始用例 JSON: {raw_json_path}")

    # ── Step 4: 运行 v2 分析器 ────────────────────────────────────────────
    print()
    analyzer = CaseDesignAnalyzer()
    analyzer.cases = cases
    analyzer.analyze()

    output_dir = os.path.join(
        PROJECT_ROOT, "workspace", "analysis", "case_design_reports", "peap_lark"
    )
    analyzer.generate_reports(output_dir=output_dir)
    analyzer.print_summary()

    # ── 额外输出：对比人工标注 vs 自动识别 ──────────────────────────────
    if auto_yes or auto_no:
        blocker_ids = set()
        for ri in analyzer.risks:
            if ri.risk_level == "BLOCKER":
                for cid in ri.case_id.split(","):
                    blocker_ids.add(cid.strip())

        false_positive = [c for c in auto_yes if c in blocker_ids]
        false_negative = [c for c in auto_no if c not in blocker_ids]

        if false_positive or false_negative:
            print("\n⚠️  人工标注 vs 分析器 差异:")
            if false_positive:
                print(f"  [可能误判为可自动化] {false_positive}")
                print("   → 分析器检测到 BLOCKER 风险，建议复核")
            if false_negative:
                print(f"  [人工标注不可自动化但分析未检出] {false_negative}")
                print("   → 可能为业务语义难以识别，建议人工确认")
        else:
            print("\n✅ 人工标注与分析器结果一致")

    print(f"\n✨ 报告输出目录: {output_dir}")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
