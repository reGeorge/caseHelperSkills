#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""平台 API 契约冒烟验证（G2 卡点）。"""

import json
import os
import sys
from datetime import datetime

import requests
import urllib3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def call(method, url, headers, **kwargs):
    resp = requests.request(method, url, headers=headers, verify=False, timeout=30, **kwargs)
    result = {
        "status_code": resp.status_code,
        "ok": resp.status_code == 200,
        "body_preview": resp.text[:300],
    }
    try:
        result["json"] = resp.json()
    except Exception:
        result["json"] = None
    return result


def main():
    base = Config.TEST_PLATFORM_URL.rstrip('/')
    headers = {"token": Config.TEST_PLATFORM_TOKEN, "Content-Type": "application/json"}

    checks = {
        "case_get": call("GET", f"{base}/case/{Config.DEFAULT_PARENT_ID}", headers),
        "flow_get": call("GET", f"{base}/flow/1", headers),
        "variables_get": call("GET", f"{base}/case/variables/65650", headers),
    }

    report = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base,
        "checks": checks,
    }

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sandbox", "workspace")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "contract_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    passed = sum(1 for item in checks.values() if item.get("ok"))
    print(f"contract smoke: {passed}/{len(checks)} passed")
    print(out_path)


if __name__ == "__main__":
    main()
