"""
Phase 1b — 目录场景化改名 + 样本用例变量修正
-----------------------------------------------
1. 将 Phase 1 已创建的目录（3 L1 + 12 L2）改为更具场景描述的名称
2. 修正样本 GTC 用例 (68158) 中过时的 username/ssid 变量值
3. 验证状态 01 的两条样本用例结构是否完整
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/sdet-skills/platform-client'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from platform_client import PlatformClient
from config import Config

# ─── 目录 ID（Phase 1 创建结果）─────────────────────────────────────────────
L1_RENAMES = {
    68142: "01-单域(单AD服务器)",
    68143: "02-父子域(ldapReferral跨域查询)",
    68144: "03-主备域(双AD高可用)",
}

L2_RENAMES = {
    # 01-单域
    68145: "01-关闭SSL_明文通信(389端口)",
    68146: "02-开启SSL_跳过证书验证(636端口)",
    68147: "03-开启SSL_公有CA证书校验(636端口)",
    68148: "04-开启SSL_私有证书校验(636端口)",
    # 02-父子域
    68149: "01-关闭SSL_明文通信(389端口)",
    68150: "02-开启SSL_跳过证书验证(636端口)",
    68151: "03-开启SSL_公有CA证书校验(636端口)",
    68152: "04-开启SSL_私有证书校验(636端口)",
    # 03-主备域
    68153: "01-关闭SSL_明文通信(389端口)",
    68154: "02-开启SSL_跳过证书验证(636端口)",
    68155: "03-开启SSL_公有CA证书校验(636端口)",
    68156: "04-开启SSL_私有证书校验(636端口)",
}

# ─── 样本用例 ID 与需修正的变量─────────────────────────────────────────────
SETUP_CASE_ID = 68157       # 状态配置用例（变量正确，只做结构验证）
GTC_CASE_ID   = 68158       # GTC 打流用例（username/ssid 需修正）

# GTC 用例中需要修正的变量（var_id 来自 Phase 1 执行输出）
GTC_VAR_FIXES = {
    134470: ("username", "ada1"),      # adyy1 → ada1（单域主域账号）
    134472: ("ssid",     "AD133"),     # ty    → AD133
}


def rename_dirs(client, renames, label):
    errors = []
    for dir_id, new_name in renames.items():
        res = client.update_directory(dir_id, name=new_name)
        if res["success"]:
            print(f"  ✅ {label} {dir_id} → '{new_name}'")
        else:
            print(f"  ❌ {label} {dir_id} 改名失败: {res['message']}")
            errors.append((dir_id, res["message"]))
        time.sleep(0.08)
    return errors


def fix_variables(client, case_id, var_fixes):
    errors = []
    for var_id, (name, new_value) in var_fixes.items():
        res = client.update_variable(
            var_id=var_id,
            value=new_value,
            case_id=case_id,
            name=name,
        )
        if res["success"]:
            print(f"  ✅ 变量 [{var_id}] {name} → '{new_value}'")
        else:
            print(f"  ❌ 变量 [{var_id}] {name} 修正失败: {res['message']}")
            errors.append((var_id, res["message"]))
    return errors


def verify_case_steps(client, case_id, label):
    res = client.list_steps(case_id)
    if res["success"]:
        steps = res["data"]
        print(f"  📋 {label} (case={case_id}) 共 {len(steps)} 个步骤：")
        for s in steps:
            print(f"     order={s.get('order')} | quoteId={s.get('quoteId')} | name={s.get('name', '')[:40]}")
    else:
        print(f"  ⚠️  无法获取步骤列表: {res['message']}")


def verify_case_vars(client, case_id, label):
    res = client.get_case_variables_v2(case_id)
    if res["success"]:
        var_list = res["data"]
        print(f"  📌 {label} (case={case_id}) 共 {len(var_list)} 个变量：")
        for v in var_list:
            print(f"     {v['name']:35s} = {v['value']}")
    else:
        print(f"  ⚠️  无法获取变量列表: {res['message']}")


def main():
    client = PlatformClient(
        base_url=Config.TEST_PLATFORM_URL,
        token=Config.TEST_PLATFORM_TOKEN,
        creator_name=Config.CREATOR_NAME,
        creator_id=str(Config.CREATOR_ID),
    )

    all_errors = []

    # ── Step 1: 改名 L1 目录 ──────────────────────────────────────────────
    print("\n═══ Step 1: L1 目录场景化改名 ═══")
    all_errors += rename_dirs(client, L1_RENAMES, "L1")

    # ── Step 2: 改名 L2 目录 ──────────────────────────────────────────────
    print("\n═══ Step 2: L2 目录场景化改名 ═══")
    all_errors += rename_dirs(client, L2_RENAMES, "L2")

    # ── Step 3: 修正 GTC 用例变量 ─────────────────────────────────────────
    print(f"\n═══ Step 3: 修正 GTC 样本用例 ({GTC_CASE_ID}) 变量 ═══")
    all_errors += fix_variables(client, GTC_CASE_ID, GTC_VAR_FIXES)

    # ── Step 4: 验证两条样本用例完整性 ────────────────────────────────────
    print(f"\n═══ Step 4: 验证样本用例完整性 ═══")
    print("\n[ 状态配置用例 ]")
    verify_case_steps(client, SETUP_CASE_ID, "状态配置用例")
    verify_case_vars(client, SETUP_CASE_ID, "状态配置用例")

    print("\n[ GTC 打流用例 ]")
    verify_case_steps(client, GTC_CASE_ID, "GTC打流用例")
    verify_case_vars(client, GTC_CASE_ID, "GTC打流用例")

    # ── 总结 ──────────────────────────────────────────────────────────────
    print(f"\n═══ 完成 ═══  错误数: {len(all_errors)}")
    if all_errors:
        print("⚠️  错误列表:")
        for e in all_errors:
            print(f"    {e}")

    # 更新 result json
    result_path = os.path.join(os.path.dirname(__file__),
                               "../../sandbox/workspace/ad_ldaps_phase1_result.json")
    with open(result_path, encoding="utf-8") as f:
        result = json.load(f)

    result["l1_dirs"] = {v: k for k, v in L1_RENAMES.items()}
    result["l2_new_names"] = {str(k): v for k, v in L2_RENAMES.items()}
    result["gtc_var_fixed"] = ["username→ada1", "ssid→AD133"]

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  结果已更新: sandbox/workspace/ad_ldaps_phase1_result.json")


if __name__ == "__main__":
    main()
