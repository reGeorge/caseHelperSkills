#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将本地 knowledge/common_cases 中的变量备注(note)回写到平台公共用例变量。

流程：
1) 读取本地公共用例 JSON（inputs 或 case_variables）
2) 调用 GET /case/variables/{case_id} 查询平台变量（拿到变量 id）
3) 对齐变量名后调用 POST /case/variable（带 id/caseId/name/value/note）更新备注
"""

import argparse
import glob
import json
import os
import sys
from typing import Dict, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(BASE_DIR)

from config import Config

platform_client_path = os.path.join(BASE_DIR, "skills", "sdet-skills", "platform-client")
sys.path.append(platform_client_path)
from platform_client import PlatformClient


def load_common_case_files() -> List[str]:
    return sorted(glob.glob(os.path.join(Config.COMMON_CASES_DIR, "*.json")))


def extract_local_notes(case_data: Dict) -> Dict[str, str]:
    vars_list = case_data.get("inputs") or case_data.get("case_variables") or []
    notes_map = {}
    for item in vars_list:
        name = item.get("name")
        note = item.get("note", "")
        if isinstance(name, str) and name.strip() and isinstance(note, str) and note.strip():
            notes_map[name.strip()] = note.strip()
    return notes_map


def main():
    parser = argparse.ArgumentParser(description="回写公共用例变量备注到平台")
    parser.add_argument("--case-id", type=int, default=None, help="仅处理单个 case_id")
    parser.add_argument("--apply", action="store_true", help="执行真实更新；默认仅预览")
    parser.add_argument("--report", default=os.path.join(BASE_DIR, "sandbox", "workspace", "variable_note_sync_report.json"), help="报告输出路径")
    args = parser.parse_args()

    client = PlatformClient(
        base_url=Config.TEST_PLATFORM_URL,
        token=Config.TEST_PLATFORM_TOKEN,
        creator_name=Config.CREATOR_NAME,
        creator_id=str(Config.CREATOR_ID),
    )

    report = {
        "apply": args.apply,
        "total_cases": 0,
        "cases_skipped": 0,
        "cases_failed": 0,
        "vars_matched": 0,
        "vars_updated": 0,
        "vars_update_failed": 0,
        "details": [],
    }

    files = load_common_case_files()
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        case_id = case_data.get("case_id")
        alias = case_data.get("alias") or os.path.basename(fp)
        if not isinstance(case_id, int):
            report["cases_skipped"] += 1
            report["details"].append({"alias": alias, "reason": "missing_case_id"})
            continue
        if args.case_id is not None and case_id != args.case_id:
            continue

        report["total_cases"] += 1
        local_notes = extract_local_notes(case_data)
        if not local_notes:
            report["cases_skipped"] += 1
            report["details"].append({"alias": alias, "case_id": case_id, "reason": "no_local_notes"})
            continue

        vars_resp = client.get_case_variables_v2(case_id)
        if not vars_resp.get("success"):
            report["cases_failed"] += 1
            report["details"].append({
                "alias": alias,
                "case_id": case_id,
                "reason": "query_failed",
                "message": vars_resp.get("message") or vars_resp.get("resMessage"),
            })
            continue

        platform_vars = vars_resp.get("data", [])
        case_updates = []
        for pv in platform_vars:
            var_name = pv.get("name")
            var_id = pv.get("id")
            if not var_name or var_name not in local_notes or not var_id:
                continue

            report["vars_matched"] += 1
            target_note = local_notes[var_name]
            current_note = (pv.get("note") or "").strip() if isinstance(pv.get("note"), str) else ""
            if target_note == current_note:
                case_updates.append({"name": var_name, "id": var_id, "status": "unchanged"})
                continue

            if not args.apply:
                case_updates.append({
                    "name": var_name,
                    "id": var_id,
                    "status": "preview",
                    "from": current_note,
                    "to": target_note,
                })
                continue

            result = client.update_variable(
                var_id=var_id,
                case_id=case_id,
                name=var_name,
                value=pv.get("value"),
                note=target_note,
            )
            if result.get("success"):
                report["vars_updated"] += 1
                case_updates.append({"name": var_name, "id": var_id, "status": "updated"})
            else:
                report["vars_update_failed"] += 1
                case_updates.append({
                    "name": var_name,
                    "id": var_id,
                    "status": "failed",
                    "message": result.get("message"),
                })

        report["details"].append({
            "alias": alias,
            "case_id": case_id,
            "matched": len(case_updates),
            "updates": case_updates,
        })

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"处理用例数: {report['total_cases']}")
    print(f"匹配变量数: {report['vars_matched']}")
    print(f"更新成功数: {report['vars_updated']}")
    print(f"更新失败数: {report['vars_update_failed']}")
    print(f"报告文件: {args.report}")


if __name__ == "__main__":
    main()
