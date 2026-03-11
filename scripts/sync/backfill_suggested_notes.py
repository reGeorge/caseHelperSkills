#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据 no_local_notes_todo.json 中的 suggested_note 回补本地 JSON 文件，
并通过平台更新接口推送到平台。
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from config import Config

platform_client_path = BASE_DIR / "skills" / "sdet-skills" / "platform-client"
sys.path.append(str(platform_client_path))
from platform_client import PlatformClient


TODO_PATH = BASE_DIR / "sandbox" / "workspace" / "no_local_notes_todo.json"


def main():
    client = PlatformClient(
        base_url=Config.TEST_PLATFORM_URL,
        token=Config.TEST_PLATFORM_TOKEN,
        creator_name=Config.CREATOR_NAME,
        creator_id=str(Config.CREATOR_ID),
    )

    with TODO_PATH.open("r", encoding="utf-8") as f:
        todo = json.load(f)

    local_updated_count = 0
    platform_updated_count = 0
    backlog = []

    for case_entry in todo.get("cases", []):
        alias = case_entry.get("alias")
        case_id = case_entry.get("case_id")
        file_path = case_entry.get("file")
        variables = case_entry.get("variables", [])

        if not variables or not file_path:
            continue

        has_suggested = any(v.get("suggested_note", "").strip() for v in variables)
        if not has_suggested:
            continue

        print(f"\n处理: {alias} (case_id={case_id})")

        # 读取本地 JSON 文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                case_data = json.load(f)
        except Exception as e:
            print(f"  ❌ 无法读取本地文件: {e}")
            continue

        # 遍历变量，更新 note
        local_changes = []
        for var in variables:
            var_name = var.get("name")
            suggested = var.get("suggested_note", "").strip()
            if not suggested:
                continue

            # 更新本地 JSON（inputs 或 case_variables）
            for field in ("inputs", "case_variables"):
                items = case_data.get(field)
                if not isinstance(items, list):
                    continue

                for item in items:
                    if item.get("name") == var_name:
                        old_note = item.get("note", "")
                        item["note"] = suggested
                        item["note_source"] = "suggested"
                        local_changes.append((var_name, old_note, suggested))
                        print(f"  ✓ 本地更新: {var_name} = '{suggested}'")
                        break

        # 保存本地 JSON
        if local_changes:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(case_data, f, ensure_ascii=False, indent=2)
                local_updated_count += len(local_changes)
                print(f"  ✓ 保存本地文件")
            except Exception as e:
                print(f"  ❌ 无法保存本地文件: {e}")
                continue

        # 推送到平台
        vars_resp = client.get_case_variables_v2(case_id)
        if not vars_resp.get("success"):
            print(f"  ❌ 查询平台变量失败: {vars_resp.get('message')}")
            backlog.append(case_entry)
            continue

        platform_vars = vars_resp.get("data", [])
        for var in variables:
            var_name = var.get("name")
            suggested = var.get("suggested_note", "").strip()
            if not suggested:
                continue

            pv = next((v for v in platform_vars if v.get("name") == var_name), None)
            if not pv:
                print(f"  ⚠️  平台无此变量: {var_name}")
                continue

            result = client.update_variable(
                var_id=pv.get("id"),
                case_id=case_id,
                name=var_name,
                value=pv.get("value"),
                note=suggested,
            )
            if result.get("success"):
                platform_updated_count += 1
                print(f"  ✓ 平台更新: {var_name}")
            else:
                print(f"  ❌ 平台更新失败: {var_name} - {result.get('message')}")

    print(f"\n\n=== 总结 ===")
    print(f"本地更新变量数: {local_updated_count}")
    print(f"平台更新变量数: {platform_updated_count}")
    if backlog:
        print(f"有 {len(backlog)} 个用例未能推送到平台")


if __name__ == "__main__":
    main()
