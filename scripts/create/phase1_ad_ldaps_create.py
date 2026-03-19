"""
Phase 1 — AD LDAPs 自动化用例创建
目标：
  1. 在父目录 68071 下构建 2 层目录（3 D1 × 4 D2 = 12 叶子节点）
  2. 在叶子节点 01（单域/关闭SSL）创建样本用例：
     - 状态配置用例（S-01 登录 + S-02 更新AD源）
     - 1x GTC 打流用例（S-11 + S-14 清理）
  3. 将结果写入 sandbox/workspace/ad_ldaps_phase1_result.json

用法：
  python -X utf8 scripts/create/phase1_ad_ldaps_create.py
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/sdet-skills/platform-client'))
sys.path.insert(0, os.path.dirname(__file__) + '/../..')

from platform_client import PlatformClient
from config import Config

# ─── 配置区 ────────────────────────────────────────────────────────────────
PARENT_DIR_ID = 68071       # 平台目标父目录

# 公共步骤 ID
S_01_LOGIN        = 51401   # 【公共】登录管理端
S_02_UPDATE_AD    = 68077   # 【公共-AD】更新 AD 认证源（通用模板）
S_11_GTC          = 67312   # 【公共】有线 1x GTC 认证 + 记账 + 下线
S_14_CLEANUP      = 55645   # 【公共】认证后下线 + 注销本地

# ─── 状态矩阵 ─────────────────────────────────────────────────────────────
#  每行：(d1_name, d2_name, ldapReferral, ad_ip_backup, ssl_enable, cert_check, cert_type, ad_port)
STATES = [
    # 01-单域
    ("01-单域", "01-关闭SSL",            "false", "",              "false", "false", "",  "389"),
    ("01-单域", "02-开启SSL(无证书校验)", "false", "",              "true",  "false", "",  "636"),
    ("01-单域", "03-开启SSL(公有证书)",   "false", "",              "true",  "true",  "0", "636"),
    ("01-单域", "04-开启SSL(私有证书)",   "false", "",              "true",  "true",  "1", "636"),
    # 02-父子域
    ("02-父子域", "01-关闭SSL",            "true",  "",              "false", "false", "",  "389"),
    ("02-父子域", "02-开启SSL(无证书校验)", "true",  "",              "true",  "false", "",  "636"),
    ("02-父子域", "03-开启SSL(公有证书)",   "true",  "",              "true",  "true",  "0", "636"),
    ("02-父子域", "04-开启SSL(私有证书)",   "true",  "",              "true",  "true",  "1", "636"),
    # 03-主备域
    ("03-主备域", "01-关闭SSL",            "false", "172.17.9.254", "false", "false", "",  "389"),
    ("03-主备域", "02-开启SSL(无证书校验)", "false", "172.17.9.254", "true",  "false", "",  "636"),
    ("03-主备域", "03-开启SSL(公有证书)",   "false", "172.17.9.254", "true",  "true",  "0", "636"),
    ("03-主备域", "04-开启SSL(私有证书)",   "false", "172.17.9.254", "true",  "true",  "1", "636"),
]

# 所有状态共用的固定变量
COMMON_VARS = {
    "ad_identitySourceName":    "172.17.9.133",
    "ad_domainName":            "rjsmpplus.com.cn",
    "ad_adminAccount":          "administrator",
    "ad_adminPassword":         "shyfzx@163",
    "ad_queryAccount":          "CN=Administrator,CN=Users,DC=rjsmpplus,DC=com,DC=cn",
    "ad_queryPassword":         "shyfzx@163",
    "ad_netbiosDomainName":     "RUIJIE",
    "ad_mainServerDomainName":  "ad1.rjsmpplus.com.cn",
    "ad_ip_primary":            "172.17.9.133",
    "adSourceId2update":        "1006",
    "groupInfoUuid_root":       "4028b64912bd24460112bd480a8a0026",
}

# 打流用例变量（所有打流共用）
FLOW_VARS = {
    "username": "adyy1",
    "password": "shyfzx@163",
    "ssid":     "ty",
    "userIP":   "10.1.1.1",
}

# ─── 工具函数 ──────────────────────────────────────────────────────────────

def add_quote_step(client, case_id, order, quote_id, name="引用步骤"):
    """添加引用公共用例的步骤"""
    res = client.create_step(
        case_id=case_id,
        name=name,
        order=order,
        type=1,
        quote_id=quote_id,
    )
    if res["success"]:
        print(f"    ✅ 步骤[{order}] quoteId={quote_id} → flow_id={res['data']}")
    else:
        print(f"    ❌ 步骤[{order}] quoteId={quote_id} 失败: {res['message']}")
    return res


def add_variables(client, case_id, var_dict):
    """批量添加变量"""
    for name, value in var_dict.items():
        res = client.create_variable(case_id, name, value)
        if res["success"]:
            print(f"    📌 变量 {name}={value!r:30s} var_id={res['data']}")
        else:
            print(f"    ⚠️  变量 {name} 失败: {res['message']}")
        time.sleep(0.05)


# ─── 主逻辑 ────────────────────────────────────────────────────────────────

def main():
    client = PlatformClient(
        base_url=Config.TEST_PLATFORM_URL,
        token=Config.TEST_PLATFORM_TOKEN,
        creator_name=Config.CREATOR_NAME,
        creator_id=str(Config.CREATOR_ID),
    )

    result = {
        "parent_dir": PARENT_DIR_ID,
        "dirs": {},          # "01-单域/01-关闭SSL" -> dir_id
        "sample_cases": {},  # "setup" / "gtc" -> case_id
        "errors": [],
    }

    # ── Step 1: 构建 2 层目录 ──────────────────────────────────────────────
    print("\n═══ Step 1: 构建目录结构 ═══")
    l1_dirs = {}  # "01-单域" -> dir_id

    d1_names = sorted(set(s[0] for s in STATES))
    for d1 in d1_names:
        res = client.create_directory(d1, parent_id=PARENT_DIR_ID)
        if res["success"]:
            l1_dirs[d1] = res["data"]
            print(f"  📁 L1: {d1} → id={res['data']}")
        else:
            print(f"  ❌ L1: {d1} 失败: {res['message']}")
            result["errors"].append({"level": "L1", "name": d1, "msg": res["message"]})
        time.sleep(0.1)

    for (d1, d2, *_) in STATES:
        if d1 not in l1_dirs:
            continue
        key = f"{d1}/{d2}"
        res = client.create_directory(d2, parent_id=l1_dirs[d1])
        if res["success"]:
            result["dirs"][key] = res["data"]
            print(f"  📂 L2: {key} → id={res['data']}")
        else:
            print(f"  ❌ L2: {key} 失败: {res['message']}")
            result["errors"].append({"level": "L2", "name": key, "msg": res["message"]})
        time.sleep(0.1)

    # ── Step 2: 在状态 01（单域/关闭SSL）创建样本用例 ──────────────────────
    sample_key = "01-单域/01-关闭SSL"
    if sample_key not in result["dirs"]:
        print(f"\n❌ 叶子目录 {sample_key} 未创建成功，跳过样本用例创建")
    else:
        leaf_id = result["dirs"][sample_key]
        state = STATES[0]
        _, _, ldapReferral, ad_ip_backup, ssl_enable, cert_check, cert_type, ad_port = state

        local_vars = {
            "ldapReferral":  ldapReferral,
            "ad_ip_backup":  ad_ip_backup,
            "ssl_enable":    ssl_enable,
            "cert_check":    cert_check,
            "cert_type":     cert_type,
            "ad_port":       ad_port,
        }

        # ── 2a. 状态配置用例 ──────────────────────────────────────────────
        print(f"\n═══ Step 2a: 创建状态配置用例 (leaf={leaf_id}) ═══")
        case_name = "01-【状态配置】[AD-单域-关闭SSL] 配置 AD 认证源为：单域-关闭SSL"
        case_res = client.create_case(
            name=case_name,
            directory_id=leaf_id,
            description=(
                "【AD LDAPs 自动化】状态配置用例 — 单域 + 关闭SSL\n"
                "依赖步骤: S-01(登录管理端), S-02(更新AD认证源)\n"
                "本用例作为同目录下所有打流用例的隐式前置配置"
            ),
            priority=2,
        )
        if not case_res["success"]:
            print(f"  ❌ 状态配置用例创建失败: {case_res['message']}")
            result["errors"].append({"type": "setup_case", "msg": case_res["message"]})
        else:
            setup_cid = case_res["data"]
            result["sample_cases"]["setup"] = setup_cid
            print(f"  ✅ 状态配置用例 id={setup_cid}")

            # 注入变量（公共 + 局部）
            all_setup_vars = {**COMMON_VARS, **local_vars}
            add_variables(client, setup_cid, all_setup_vars)

            # 添加引用步骤：S-01 → S-02
            add_quote_step(client, setup_cid, 1, S_01_LOGIN,     "【公共】登录管理端")
            add_quote_step(client, setup_cid, 2, S_02_UPDATE_AD, "【公共-AD】更新 AD 认证源（单域-关闭SSL）")

        # ── 2b. 1x GTC 打流用例 ───────────────────────────────────────────
        print(f"\n═══ Step 2b: 创建 1x GTC 打流用例 (leaf={leaf_id}) ═══")
        gtc_name = "03-【AD-LDAPs-GTC-01】单域+关闭SSL 用户 1x GTC 认证学习到本地"
        gtc_res = client.create_case(
            name=gtc_name,
            directory_id=leaf_id,
            description=(
                "【AD LDAPs 自动化】1x GTC 打流用例 — 单域 + 关闭SSL\n"
                "依赖步骤: S-11(有线1x GTC认证+记账+下线), S-14(清理)\n"
                "前置条件: 需先运行同目录下的状态配置用例"
            ),
            priority=2,
        )
        if not gtc_res["success"]:
            print(f"  ❌ GTC 打流用例创建失败: {gtc_res['message']}")
            result["errors"].append({"type": "gtc_case", "msg": gtc_res["message"]})
        else:
            gtc_cid = gtc_res["data"]
            result["sample_cases"]["gtc"] = gtc_cid
            print(f"  ✅ GTC 打流用例 id={gtc_cid}")

            # 注入变量（打流变量）
            add_variables(client, gtc_cid, FLOW_VARS)

            # 添加引用步骤：S-11 → S-14
            add_quote_step(client, gtc_cid, 1, S_11_GTC,     "【公共】有线1x GTC认证+记账+下线")
            add_quote_step(client, gtc_cid, 2, S_14_CLEANUP, "【公共】认证后下线+注销本地")

    # ── 保存结果 ────────────────────────────────────────────────────────────
    out_path = os.path.join(os.path.dirname(__file__), "../../sandbox/workspace/ad_ldaps_phase1_result.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n═══ 完成 ═══")
    print(f"  目录数: {len(result['dirs'])} / 12")
    print(f"  样本用例: {result['sample_cases']}")
    print(f"  错误数: {len(result['errors'])}")
    print(f"  结果已保存: sandbox/workspace/ad_ldaps_phase1_result.json")

    if result["errors"]:
        print("\n⚠️  错误列表:")
        for e in result["errors"]:
            print(f"    {e}")


if __name__ == "__main__":
    main()
