#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地知识库变量备注初始化脚本
用途：遍历 knowledge/common_cases/*.json，对 case_variables/inputs 中缺失 note 的变量做初始化。
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMON_CASES_DIR = ROOT / "knowledge" / "common_cases"


def infer_variable_note(var_name):
    if not var_name:
        return ""

    normalized = str(var_name).strip().lower()
    note_rules = [
        (["username", "user_name", "userid", "user_id", "eap_username", "usernam"], "认证用户名"),
        (["password", "pwd", "pass", "eap_password"], "认证密码"),
        (["token", "access_token", "app_access_token"], "访问令牌"),
        (["session", "sessionid", "sid"], "会话ID"),
        (["uuid", "guid"], "资源UUID"),
        (["group", "groupid", "group_uuid"], "用户组标识"),
        (["mac"], "终端MAC地址"),
        (["ip", "nasip", "userip"], "IP地址"),
    ]

    for keys, note in note_rules:
        if any(k in normalized for k in keys):
            return note

    return ""


def normalize_var_item(item):
    raw_note = item.get("note")
    note = raw_note.strip() if isinstance(raw_note, str) else ""
    source = item.get("note_source", "platform")

    if not note:
        note = infer_variable_note(item.get("name"))
        source = "inferred" if note else "empty"

    item["note"] = note
    item["note_source"] = source
    return source == "inferred"


def process_file(file_path):
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    inferred_count = 0

    for field in ("case_variables", "inputs"):
        variables = data.get(field)
        if not isinstance(variables, list):
            continue

        for item in variables:
            if not isinstance(item, dict):
                continue

            before_note = item.get("note")
            before_source = item.get("note_source")
            inferred_now = normalize_var_item(item)

            if item.get("note") != before_note or item.get("note_source") != before_source:
                changed = True
            if inferred_now:
                inferred_count += 1

    if changed:
        sync_meta = data.get("sync_metadata")
        if not isinstance(sync_meta, dict):
            sync_meta = {}
            data["sync_metadata"] = sync_meta

        sync_meta["note_initialized_count"] = inferred_count

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return changed, inferred_count


def main():
    if not COMMON_CASES_DIR.exists():
        print(f"目录不存在: {COMMON_CASES_DIR}")
        return

    files = sorted(COMMON_CASES_DIR.glob("*.json"))
    changed_files = 0
    total_inferred = 0

    for file_path in files:
        changed, inferred_count = process_file(file_path)
        if changed:
            changed_files += 1
            total_inferred += inferred_count

    print(f"扫描文件数: {len(files)}")
    print(f"发生修改文件数: {changed_files}")
    print(f"自动初始化 note 数量: {total_inferred}")


if __name__ == "__main__":
    main()
