"""
Phase 1+2 全量创建 — AD LDAPs 自动化用例
目标父目录: 68176
创建: 12 叶子目录 + 60 条用例（12 状态配置 + 48 打流）

变量注入修正:
  Portal  → Portal_username / Portal_password / userId2test / ssid / userIP
  GTC     → peap_username / peap_password / userId2test / ssid / userIP
  MschapV2→ peap_username(大写) / peap_password / src_username(小写) / userId2test(大写) / ssid / userIP
  TTLS-PAP→ peap_username / peap_password / userId2test / ssid / userIP
"""

import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/sdet-skills/platform-client'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from platform_client import PlatformClient
from config import Config

# ─── 配置 ──────────────────────────────────────────────────────────────────
PARENT_DIR_ID  = 68176

S_01_LOGIN     = 51401
S_02_UPDATE_AD = 68077
S_10_PORTAL    = 62033
S_11_GTC       = 67312
S_12_MSCHAPV2  = 67314
S_13_TTLSPAP   = 67313
S_14_CLEANUP   = 55645

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

SSID   = "AD133"
USERIP = "10.1.1.1"

# ─── 12 基准状态 ─────────────────────────────────────────────────────────
# (l1目录名, l2目录名, d1标签, d2标签, ldapReferral, ad_ip_backup, ssl_enable, cert_check, cert_type, ad_port, flow_username, flow_password)
STATES = [
    # 01-单域
    ("01-单域(单AD服务器)",          "01-关闭SSL_明文通信(389端口)",       "单域",   "关闭SSL",         "false", "",              "false", "false", "",  "389", "ada1",    "shyfzx@163"),
    ("01-单域(单AD服务器)",          "02-开启SSL_跳过证书验证(636端口)",   "单域",   "开启SSL无证书校验","false", "",              "true",  "false", "",  "636", "ada1",    "shyfzx@163"),
    ("01-单域(单AD服务器)",          "03-开启SSL_公有CA证书校验(636端口)", "单域",   "开启SSL公有证书",  "false", "",              "true",  "true",  "0", "636", "ada1",    "shyfzx@163"),
    ("01-单域(单AD服务器)",          "04-开启SSL_私有证书校验(636端口)",   "单域",   "开启SSL私有证书",  "false", "",              "true",  "true",  "1", "636", "ada1",    "shyfzx@163"),
    # 02-父子域
    ("02-父子域(ldapReferral跨域查询)", "01-关闭SSL_明文通信(389端口)",       "父子域", "关闭SSL",         "true",  "",              "false", "false", "",  "389", "testsec", "shyfzx@163"),
    ("02-父子域(ldapReferral跨域查询)", "02-开启SSL_跳过证书验证(636端口)",   "父子域", "开启SSL无证书校验","true",  "",              "true",  "false", "",  "636", "testsec", "shyfzx@163"),
    ("02-父子域(ldapReferral跨域查询)", "03-开启SSL_公有CA证书校验(636端口)", "父子域", "开启SSL公有证书",  "true",  "",              "true",  "true",  "0", "636", "testsec", "shyfzx@163"),
    ("02-父子域(ldapReferral跨域查询)", "04-开启SSL_私有证书校验(636端口)",   "父子域", "开启SSL私有证书",  "true",  "",              "true",  "true",  "1", "636", "testsec", "shyfzx@163"),
    # 03-主备域
    ("03-主备域(双AD高可用)",         "01-关闭SSL_明文通信(389端口)",       "主备域", "关闭SSL",         "false", "172.17.9.254",  "false", "false", "",  "389", "ada1",    "shyfzx@163"),
    ("03-主备域(双AD高可用)",         "02-开启SSL_跳过证书验证(636端口)",   "主备域", "开启SSL无证书校验","false", "172.17.9.254",  "true",  "false", "",  "636", "ada1",    "shyfzx@163"),
    ("03-主备域(双AD高可用)",         "03-开启SSL_公有CA证书校验(636端口)", "主备域", "开启SSL公有证书",  "false", "172.17.9.254",  "true",  "true",  "0", "636", "ada1",    "shyfzx@163"),
    ("03-主备域(双AD高可用)",         "04-开启SSL_私有证书校验(636端口)",   "主备域", "开启SSL私有证书",  "false", "172.17.9.254",  "true",  "true",  "1", "636", "ada1",    "shyfzx@163"),
]

# ─── 每种打流类型的变量覆盖映射 ────────────────────────────────────────────
def flow_vars_portal(u, p):
    return {"Portal_username": u, "Portal_password": p, "userId2test": u, "ssid": SSID, "userIP": USERIP}

def flow_vars_gtc(u, p):
    return {"peap_username": u, "peap_password": p, "userId2test": u, "ssid": SSID, "userIP": USERIP}

def flow_vars_mschapv2(u, p):
    return {"peap_username": u.upper(), "peap_password": p, "src_username": u.lower(),
            "userId2test": u.upper(), "ssid": SSID, "userIP": USERIP}

def flow_vars_ttlspap(u, p):
    return {"peap_username": u, "peap_password": p, "userId2test": u, "ssid": SSID, "userIP": USERIP}

# ─── 工具函数 ──────────────────────────────────────────────────────────────
def add_quote(client, case_id, order, quote_id):
    res = client.create_step(case_id=case_id, name="", order=order, type=1, quote_id=quote_id)
    ok = "✅" if res["success"] else "❌"
    print(f"      {ok} step[{order}] quoteId={quote_id}  flow_id={res.get('data','?') if res['success'] else res['message']}")
    return res["success"]

def inject_vars(client, case_id, var_dict):
    for name, value in var_dict.items():
        res = client.create_variable(case_id, name, value)
        if not res["success"]:
            print(f"      ⚠️  var {name} 失败: {res['message']}")

def override_inherited_vars(client, case_id, overrides: dict):
    """查询 case 现有变量，对 overrides 中的 key 执行 update；新 key 执行 create"""
    res = client.get_case_variables_v2(case_id)
    existing = {}
    if res["success"]:
        for v in res["data"]:
            existing[v["name"]] = v["id"]

    for name, value in overrides.items():
        if name in existing:
            r = client.update_variable(existing[name], value=value, case_id=case_id, name=name)
            status = "✅ upd" if r["success"] else f"❌ upd {r['message']}"
        else:
            r = client.create_variable(case_id, name, value)
            status = "✅ new" if r["success"] else f"❌ new {r['message']}"
        print(f"      {status}  {name}={repr(value)}")

def create_flow_case(client, leaf_dir_id, case_name, step_ids: list, flow_var_fn, u, p, log_prefix):
    """创建打流用例：建用例 → 加引用步骤 → 等待变量继承 → 覆盖认证变量"""
    print(f"\n    {log_prefix}")
    res = client.create_case(name=case_name, directory_id=leaf_dir_id, priority=2)
    if not res["success"]:
        print(f"      ❌ 创建失败: {res['message']}")
        return None
    cid = res["data"]
    print(f"      case_id={cid}")

    for order, qid in enumerate(step_ids, 1):
        add_quote(client, cid, order, qid)
    time.sleep(0.3)   # 等平台写入 inherited vars

    overrides = flow_var_fn(u, p)
    override_inherited_vars(client, cid, overrides)
    return cid

# ─── 主逻辑 ────────────────────────────────────────────────────────────────
def main():
    client = PlatformClient(
        base_url=Config.TEST_PLATFORM_URL,
        token=Config.TEST_PLATFORM_TOKEN,
        creator_name=Config.CREATOR_NAME,
        creator_id=str(Config.CREATOR_ID),
    )

    result = {"parent_dir": PARENT_DIR_ID, "l1_dirs": {}, "l2_dirs": {}, "cases": [], "errors": []}

    # ── Phase 1: 构建目录 ──────────────────────────────────────────────────
    print("\n═══════ Phase 1: 目录构建 ═══════")
    l1_map = {}   # l1_name → dir_id
    l2_map = {}   # (l1_name, l2_name) → dir_id

    for l1 in sorted(set(s[0] for s in STATES)):
        if l1 in l1_map:
            continue
        r = client.create_directory(l1, parent_id=PARENT_DIR_ID)
        if r["success"]:
            l1_map[l1] = r["data"]
            result["l1_dirs"][l1] = r["data"]
            print(f"  📁 L1: {l1} → {r['data']}")
        else:
            print(f"  ❌ L1: {l1} → {r['message']}")
            result["errors"].append({"type": "dir_l1", "name": l1, "msg": r["message"]})
        time.sleep(0.1)

    for (l1, l2, *_) in STATES:
        if l1 not in l1_map:
            continue
        if (l1, l2) in l2_map:
            continue
        r = client.create_directory(l2, parent_id=l1_map[l1])
        if r["success"]:
            l2_map[(l1, l2)] = r["data"]
            result["l2_dirs"][f"{l1}/{l2}"] = r["data"]
            print(f"  📂 L2: {l1}/{l2} → {r['data']}")
        else:
            print(f"  ❌ L2: {l1}/{l2} → {r['message']}")
            result["errors"].append({"type": "dir_l2", "name": f"{l1}/{l2}", "msg": r["message"]})
        time.sleep(0.1)

    # ── Phase 2: 全量用例创建 ──────────────────────────────────────────────
    print("\n═══════ Phase 2: 全量用例创建 ═══════")

    for idx, state in enumerate(STATES, 1):
        l1, l2, d1, d2, ldapRef, ip_bak, ssl_en, cert_chk, cert_tp, ad_port, flow_u, flow_p = state
        key = f"{l1}/{l2}"
        leaf_id = l2_map.get((l1, l2))
        if not leaf_id:
            print(f"\n  ⚠️  跳过 {key}（目录未创建）")
            continue

        tag = f"[{idx:02d}] {d1}+{d2}"
        print(f"\n{'─'*60}")
        print(f"  🗂  {tag}  leaf={leaf_id}")

        case_ids = {"state": idx, "l1": l1, "l2": l2, "leaf_id": leaf_id}

        # 1. 状态配置用例
        setup_name = f"01-【状态配置】配置AD认证源：{d1}+{d2}"
        print(f"\n    [状态配置] {setup_name}")
        r = client.create_case(name=setup_name, directory_id=leaf_id, priority=2,
                               description=f"配置 AD 认证源为 {d1}+{d2}\n前置步骤: S-01登录→S-02更新AD源")
        if not r["success"]:
            print(f"      ❌ 创建失败: {r['message']}")
            result["errors"].append({"type": "case_setup", "state": idx, "msg": r["message"]})
        else:
            scid = r["data"]
            case_ids["setup"] = scid
            print(f"      case_id={scid}")
            # 注入变量
            setup_all_vars = {**COMMON_VARS,
                              "ldapReferral": ldapRef, "ad_ip_backup": ip_bak,
                              "ssl_enable": ssl_en, "cert_check": cert_chk,
                              "cert_type": cert_tp, "ad_port": ad_port}
            inject_vars(client, scid, setup_all_vars)
            # 引用步骤
            add_quote(client, scid, 1, S_01_LOGIN)
            add_quote(client, scid, 2, S_02_UPDATE_AD)

        time.sleep(0.15)

        # 2. Portal 打流
        portal_name = f"02-【AD认证-Portal】{d1}+{d2} Portal认证学习到本地"
        cid = create_flow_case(client, leaf_id, portal_name,
                               [S_10_PORTAL, S_14_CLEANUP], flow_vars_portal, flow_u, flow_p,
                               f"[Portal] {portal_name}")
        if cid:
            case_ids["portal"] = cid

        time.sleep(0.15)

        # 3. GTC 打流
        gtc_name = f"03-【AD认证-1xGTC】{d1}+{d2} 1xGTC认证学习到本地"
        cid = create_flow_case(client, leaf_id, gtc_name,
                               [S_11_GTC, S_14_CLEANUP], flow_vars_gtc, flow_u, flow_p,
                               f"[GTC] {gtc_name}")
        if cid:
            case_ids["gtc"] = cid

        time.sleep(0.15)

        # 4. MschapV2 打流
        ms_name = f"04-【AD认证-1xMSCHAPv2】{d1}+{d2} 1xMSCHAPv2认证学习到本地"
        cid = create_flow_case(client, leaf_id, ms_name,
                               [S_12_MSCHAPV2, S_14_CLEANUP], flow_vars_mschapv2, flow_u, flow_p,
                               f"[MschapV2] {ms_name}")
        if cid:
            case_ids["mschapv2"] = cid

        time.sleep(0.15)

        # 5. TTLS-PAP 打流
        ttls_name = f"05-【AD认证-1xTTLS-PAP】{d1}+{d2} 1xTTLS-PAP认证学习到本地"
        cid = create_flow_case(client, leaf_id, ttls_name,
                               [S_13_TTLSPAP, S_14_CLEANUP], flow_vars_ttlspap, flow_u, flow_p,
                               f"[TTLS-PAP] {ttls_name}")
        if cid:
            case_ids["ttlspap"] = cid

        result["cases"].append(case_ids)
        time.sleep(0.1)

    # ── 保存 ───────────────────────────────────────────────────────────────
    out = os.path.join(os.path.dirname(__file__), "../../sandbox/workspace/ad_ldaps_phase2_result.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    setup_ok   = sum(1 for c in result["cases"] if "setup"    in c)
    portal_ok  = sum(1 for c in result["cases"] if "portal"   in c)
    gtc_ok     = sum(1 for c in result["cases"] if "gtc"      in c)
    ms_ok      = sum(1 for c in result["cases"] if "mschapv2" in c)
    ttls_ok    = sum(1 for c in result["cases"] if "ttlspap"  in c)
    total_case = setup_ok + portal_ok + gtc_ok + ms_ok + ttls_ok

    print(f"\n{'═'*60}")
    print(f"  目录: L1={len(result['l1_dirs'])}/3  L2={len(result['l2_dirs'])}/12")
    print(f"  用例: 状态配置={setup_ok}/12  Portal={portal_ok}/12")
    print(f"        GTC={gtc_ok}/12  MschapV2={ms_ok}/12  TTLS-PAP={ttls_ok}/12")
    print(f"  **合计: {total_case}/60 条**")
    print(f"  错误: {len(result['errors'])} 条")
    print(f"  结果: sandbox/workspace/ad_ldaps_phase2_result.json")

    if result["errors"]:
        print("\n⚠️  错误列表:")
        for e in result["errors"]:
            print(f"    {e}")


if __name__ == "__main__":
    main()
