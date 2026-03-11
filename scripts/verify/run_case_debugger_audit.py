#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用版本化 config_rules 执行 case-debugger 审计（G3 卡点）。"""

import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'sdet-skills', 'case-debugger'))

from case_debugger import CaseDebugger


def main():
    rules_path = os.path.join(PROJECT_ROOT, 'knowledge', 'audit', 'config_rules.json')
    with open(rules_path, 'r', encoding='utf-8-sig') as f:
        rules = json.load(f)

    debugger = CaseDebugger(
        business_dir_id=67136,
        common_dir_id=66880,
        config_rules=rules,
        dry_run=True,
    )
    report = debugger.run_full_audit()
    print(f"audit completed: total={report.total_cases}, deviated={len(report.deviated_cases)}")


if __name__ == '__main__':
    main()
