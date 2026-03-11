#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 variable_note_sync_report.json 中提取 no_local_notes 用例，
生成待补备注清单（JSON + Markdown）。
"""

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "sandbox" / "workspace" / "variable_note_sync_report.json"
COMMON_CASES_DIR = ROOT / "knowledge" / "common_cases"
OUT_JSON = ROOT / "sandbox" / "workspace" / "no_local_notes_todo.json"
OUT_MD = ROOT / "sandbox" / "workspace" / "no_local_notes_todo.md"


def infer_variable_note(var_name):
    if not var_name:
        return ""

    normalized = str(var_name).strip().lower()
    note_rules = [
        (["username", "user_name", "userid", "user_id", "eap_username", "portal_username", "peap_username"], "认证用户名"),
        (["password", "pwd", "pass", "eap_password", "portal_password", "peap_password"], "认证密码"),
        (["token", "access_token", "app_access_token"], "访问令牌"),
        (["session", "sessionid", "sid"], "会话ID"),
        (["uuid", "guid"], "资源UUID"),
        (["group", "groupid", "group_uuid"], "用户组标识"),
        (["mac"], "终端MAC地址"),
        (["ip", "nasip", "userip"], "IP地址"),
        (["ssid"], "无线网络名称"),
        (["vlan"], "VLAN信息"),
    ]

    for keys, note in note_rules:
        if any(k in normalized for k in keys):
            return note
    return ""


def load_case_by_alias(alias):
    path = COMMON_CASES_DIR / f"{alias}.json"
    if not path.exists():
        return None, str(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f), str(path)


def main():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"报告不存在: {REPORT_PATH}")

    with REPORT_PATH.open("r", encoding="utf-8") as f:
        report = json.load(f)

    details = report.get("details", [])
    targets = [d for d in details if d.get("reason") == "no_local_notes"]

    out = {
        "total_cases": len(targets),
        "cases": []
    }

    md_lines = [
        "# no_local_notes 待补备注清单",
        "",
        f"总用例数: {len(targets)}",
        "",
    ]

    for item in targets:
        alias = item.get("alias", "")
        case_id = item.get("case_id")
        case_data, case_path = load_case_by_alias(alias)

        case_entry = {
            "alias": alias,
            "case_id": case_id,
            "file": case_path,
            "variables": []
        }

        md_lines.append(f"## {alias} (case_id={case_id})")

        if not case_data:
            md_lines.append("- 文件不存在，需人工确认")
            md_lines.append("")
            out["cases"].append(case_entry)
            continue

        vars_list = case_data.get("inputs") or case_data.get("case_variables") or []
        if not vars_list:
            md_lines.append("- 无变量，跳过")
            md_lines.append("")
            out["cases"].append(case_entry)
            continue

        for var in vars_list:
            name = var.get("name")
            note = (var.get("note") or "").strip() if isinstance(var.get("note"), str) else ""
            suggestion = infer_variable_note(name)
            entry = {
                "name": name,
                "current_note": note,
                "suggested_note": suggestion
            }
            case_entry["variables"].append(entry)
            md_lines.append(f"- {name}: 当前备注='{note}' | 建议备注='{suggestion}'")

        md_lines.append("")
        out["cases"].append(case_entry)

    os.makedirs(OUT_JSON.parent, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"已生成: {OUT_JSON}")
    print(f"已生成: {OUT_MD}")
    print(f"统计: {out['total_cases']} 个用例")


if __name__ == "__main__":
    main()
