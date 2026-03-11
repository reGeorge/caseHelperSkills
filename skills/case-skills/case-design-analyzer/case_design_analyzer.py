#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Case Design Analyzer v2 — 测试架构师级用例设计分析器

重构自 v1 的"数词机器人"，核心改进:
  Layer 1: BusinessClusterer  — 碎片UI步骤 → 业务动作序列
  Layer 2: DimensionMiner     — 自适应维度归纳 + 笛卡尔积缺口检测
  Layer 3: ApiAligner         — 对齐已有公共步骤/API定义，标注遗漏参数和类型陷阱
  Layer 4: DualVerifier       — 预期结果拆解为「前端表现」+「后端真相」
  Layer 5: RiskTagger         — 物理依赖/时序依赖/不可自动化标记

设计原则来自 knowledge/case_design/insight.md 的血泪教训:
  - 先穷举状态组合，再建公共步骤，最后批量生成业务用例
  - method 字段是 int 不是 str
  - body 序列化只在 platform_client 内部做一次
  - dict key lookup 时 int vs str 必须统一

输出目录: workspace/analysis/case_design_reports/
"""

import json
import re
import os
import sys
import itertools
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ─────────────────────────── Data Models ───────────────────────────

@dataclass
class ManualCase:
    case_id: str
    case_title: str
    precondition: str
    steps: List[Dict]
    expected_result: str


@dataclass
class Intent:
    """步骤意图标签"""
    label: str        # NAVIGATE / SELECT / INPUT / EXECUTE / WAIT / VERIFY / PHYSICAL
    raw_text: str
    data_hint: str = ""  # 识别到的数据注入信息


@dataclass
class BusinessAction:
    """聚类后的业务动作"""
    action_id: str
    name: str
    intent_pattern: Tuple[str, ...]
    raw_steps: List[str]
    data_injections: List[str]
    case_ids: List[str]
    parameterizable: bool = True


@dataclass
class Dimension:
    """维度"""
    name: str
    values: List[str]
    dim_type: str = "enum"       # enum / boolean / numeric
    source: str = "precondition"
    api_field: str = ""


@dataclass
class CartesianGap:
    """笛卡尔积缺口"""
    combination: Dict[str, str]
    covered: bool
    matched_case_id: str = ""


@dataclass
class DualVerification:
    """双重验证条目"""
    case_id: str
    raw_expected: str
    frontend_assertions: List[str]
    backend_assertions: List[str]
    missing_backend: bool = False


@dataclass
class ApiAlignment:
    """API对齐条目"""
    dimension_name: str
    matched_common_step: str = ""
    matched_case_id: int = 0
    required_inputs: List[str] = field(default_factory=list)
    missing_inputs: List[str] = field(default_factory=list)
    type_traps: List[str] = field(default_factory=list)


@dataclass
class RiskItem:
    """风险条目"""
    case_id: str
    case_title: str
    risk_level: str    # BLOCKER / HIGH / MEDIUM
    risk_type: str     # PHYSICAL / TIMING / ENVIRONMENT / TYPE_TRAP
    description: str
    suggestion: str


# ─────────────────────────── Layer 1: BusinessClusterer ───────────────────────────

class BusinessClusterer:
    """将碎片UI步骤映射为业务动作序列"""

    # 意图标签 → 匹配模式（优先级从高到低）
    INTENT_RULES = [
        ("PHYSICAL",  r'移动设备|拔插|拔出|插入|断电|重启|物理|硬件|手动操作|人工|掉电'),
        ("VERIFY",    r'验证|检查|查看|确认|断言|观察|应该|是否|显示为'),
        ("WAIT",      r'等待|直到|超时|超过.*[天日时分秒]|过期|有效期|经过|N天后'),
        ("INPUT",     r'输入|填写|填入|设置.*为|配置.*为|修改.*为'),
        ("SELECT",    r'选择|选中|勾选|点选|切换到'),
        ("NAVIGATE",  r'打开|进入|跳转|返回|切换.*页面|登录.*页面'),
        ("EXECUTE",   r'点击|提交|确认|保存|发送|连接|断开|启用|禁用|开启|关闭'),
    ]

    DATA_PATTERN = re.compile(
        r'(?:输入|填写|设置.*?为|密码[：:]|用户名[：:]|SSID[：:])\s*[：:]*\s*(\S+)',
        re.IGNORECASE
    )

    def classify_intent(self, step_text: str) -> Intent:
        for label, pattern in self.INTENT_RULES:
            if re.search(pattern, step_text, re.IGNORECASE):
                data_hint = ""
                m = self.DATA_PATTERN.search(step_text)
                if m:
                    data_hint = m.group(1)
                return Intent(label=label, raw_text=step_text, data_hint=data_hint)
        return Intent(label="OTHER", raw_text=step_text)

    def cluster(self, cases: List[ManualCase]) -> List[BusinessAction]:
        case_intents: Dict[str, List[Intent]] = {}
        for case in cases:
            intents = [self.classify_intent(s.get("description", "")) for s in case.steps]
            case_intents[case.case_id] = intents

        pattern_groups: Dict[Tuple, List[str]] = defaultdict(list)
        pattern_details: Dict[Tuple, Dict] = {}

        for case_id, intents in case_intents.items():
            op_intents = [i for i in intents if i.label != "VERIFY"]
            pattern = tuple(i.label for i in op_intents)
            pattern_groups[pattern].append(case_id)
            if pattern not in pattern_details:
                pattern_details[pattern] = {
                    "raw_steps": [i.raw_text for i in op_intents],
                    "data_injections": [i.data_hint for i in op_intents if i.data_hint],
                }

        actions = []
        for idx, (pattern, case_ids) in enumerate(
            sorted(pattern_groups.items(), key=lambda x: len(x[1]), reverse=True)
        ):
            details = pattern_details[pattern]
            name = self._generate_action_name(pattern, details["raw_steps"])
            actions.append(BusinessAction(
                action_id=f"BA_{idx:03d}",
                name=name,
                intent_pattern=pattern,
                raw_steps=details["raw_steps"],
                data_injections=details["data_injections"],
                case_ids=case_ids,
                parameterizable=("PHYSICAL" not in pattern and "WAIT" not in pattern),
            ))

        return actions

    def _generate_action_name(self, pattern: Tuple, raw_steps: List[str]) -> str:
        if "PHYSICAL" in pattern:
            return f"物理操作: {raw_steps[0][:30]}"
        if "WAIT" in pattern:
            wait_step = next((s for s in raw_steps if re.search(r'等待|超过|有效期|过期', s)), raw_steps[-1])
            return f"时间依赖等待: {wait_step[:40]}"
        has_input = "INPUT" in pattern
        has_navigate = "NAVIGATE" in pattern
        has_execute = "EXECUTE" in pattern

        target = ""
        for s in raw_steps:
            m = re.search(r"选择['\"]?(\S+?)['\"]?", s)
            if m:
                target = m.group(1)
                break

        if has_navigate and has_input and has_execute:
            return f"执行带参数操作" + (f"→{target}" if target else "")
        elif has_navigate and has_execute:
            return f"执行操作" + (f"→{target}" if target else "")
        else:
            return f"组合操作({'→'.join(set(pattern))})"


# ─────────────────────────── Layer 2: DimensionMiner ───────────────────────────

class DimensionMiner:
    """自适应维度归纳 + 笛卡尔积缺口检测"""

    OPPOSITION_PAIRS = [
        ("成功", "失败"), ("开启", "关闭"), ("正确", "错误"),
        ("有效", "无效"), ("允许", "禁止"), ("连接", "断开"),
        ("认证通过", "认证失败"), ("正常", "异常"),
    ]

    def mine(self, cases: List[ManualCase]) -> Tuple[List[Dimension], List[CartesianGap]]:
        case_attrs: Dict[str, Dict[str, str]] = {}
        for case in cases:
            attrs = {}
            attrs.update(self._extract_from_precondition(case.precondition))
            attrs.update(self._extract_from_title(case.case_title, cases))
            case_attrs[case.case_id] = attrs

        # 对所有属性 key 做聚合，多值 key = 维度
        all_keys: Dict[str, Set[str]] = defaultdict(set)
        for attrs in case_attrs.values():
            for k, v in attrs.items():
                all_keys[k].add(v)

        dimensions = []
        for key, values in all_keys.items():
            if len(values) >= 2:
                dim = Dimension(
                    name=key,
                    values=sorted(list(values)),
                    dim_type="boolean" if values <= {"开启", "关闭", "是", "否"} else "enum",
                    source="mixed",
                )
                dimensions.append(dim)

        gaps = self._detect_cartesian_gaps(dimensions, case_attrs)
        return dimensions, gaps

    def _extract_from_precondition(self, precondition: str) -> Dict[str, str]:
        attrs = {}

        if re.search(r'有线|以太网|LAN', precondition, re.IGNORECASE):
            attrs["网络类型"] = "有线"
        elif re.search(r'WiFi|无线|WLAN|SSID', precondition, re.IGNORECASE):
            attrs["网络类型"] = "无线"

        auth_map = [
            (r'DOT1X|802\.?1[xX]', "DOT1X"),
            (r'WPA2', "WPA2"),
            (r'WPA(?!2)', "WPA"),
            (r'开放式|OPEN|无认证', "OPEN"),
            (r'MAB|无感', "MAB"),
            (r'Portal|web认证', "Portal"),
        ]
        for pattern, value in auth_map:
            if re.search(pattern, precondition, re.IGNORECASE):
                attrs["认证方式"] = value
                break

        role_map = [
            (r'(?:管理员|admin)\s*(?:权限|身份|角色)?', "admin"),
            (r'(?:普通用户|guest)\s*(?:权限|身份|角色)?', "guest"),
        ]
        for pattern, value in role_map:
            if re.search(pattern, precondition, re.IGNORECASE):
                attrs["用户身份"] = value
                break

        state_map = [
            (r'处于未连接|未连接状态', "未连接"),
            (r'已连接|处于连接状态', "已连接"),
            (r'已认证|处于认证', "已认证"),
            (r'WiFi关闭|关闭状态', "关闭"),
        ]
        for pattern, value in state_map:
            if re.search(pattern, precondition, re.IGNORECASE):
                attrs["设备初始状态"] = value
                break

        if re.search(r'简单密码|密码为\d{3,6}\b', precondition):
            attrs["密码复杂度"] = "简单"
        elif re.search(r'复杂密码|大小写.*数字.*特殊字符|[!@#$%^&*]', precondition):
            attrs["密码复杂度"] = "复杂"

        # 通用开关维度（dot1x密码策略场景）
        switch_patterns = [
            ("首次登录强制修改", r'首次.*开启|首次.*强制', r'首次.*关闭|不启用首次'),
            ("弱密码强制处理", r'弱密码.*开启|强度.*开启', r'弱密码.*关闭|强度.*关闭'),
            ("定时强制修改", r'定时.*开启|周期.*开启', r'定时.*关闭|周期.*关闭'),
        ]
        for dim_name, on_pat, off_pat in switch_patterns:
            if re.search(on_pat, precondition, re.IGNORECASE):
                attrs[dim_name] = "开启"
            elif re.search(off_pat, precondition, re.IGNORECASE):
                attrs[dim_name] = "关闭"

        return attrs

    def _extract_from_title(self, title: str, all_cases: List[ManualCase]) -> Dict[str, str]:
        attrs = {}
        for pos, neg in self.OPPOSITION_PAIRS:
            if pos in title:
                attrs["预期结局"] = pos
                break
            elif neg in title:
                attrs["预期结局"] = neg
                break
        return attrs

    def _detect_cartesian_gaps(
        self,
        dimensions: List[Dimension],
        case_attrs: Dict[str, Dict[str, str]],
    ) -> List[CartesianGap]:
        if not dimensions:
            return []

        dim_names = [d.name for d in dimensions]
        dim_values = [d.values for d in dimensions]

        total_combos = 1
        for v in dim_values:
            total_combos *= len(v)
            if total_combos > 512:
                break

        if total_combos > 512:
            return [CartesianGap(
                combination={"_summary": f"组合总数≥{total_combos}，超过阈值512，建议分业务场景分析"},
                covered=False,
            )]

        all_combos = list(itertools.product(*dim_values))

        case_combos: Set[Tuple] = set()
        combo_to_case: Dict[Tuple, str] = {}
        for case_id, attrs in case_attrs.items():
            combo = tuple(attrs.get(dn, "*") for dn in dim_names)
            case_combos.add(combo)
            combo_to_case[combo] = case_id

        gaps = []
        for combo in all_combos:
            matched = False
            matched_id = ""
            for cc in case_combos:
                if all(cc[i] == combo[i] or cc[i] == "*" for i in range(len(combo))):
                    matched = True
                    matched_id = combo_to_case.get(cc, "")
                    break
            gaps.append(CartesianGap(
                combination=dict(zip(dim_names, combo)),
                covered=matched,
                matched_case_id=matched_id,
            ))

        return gaps


# ─────────────────────────── Layer 3: ApiAligner ───────────────────────────

class ApiAligner:
    """对齐维度与已有公共步骤/API定义，标注类型陷阱"""

    # 来自复盘§2.* 的不变型陷阱清单
    TYPE_TRAP_RULES = [
        ("method字段必须传 int(0=GET/1=POST/2=PUT/3=DELETE)，不能传字符串 'POST'", "§2.1"),
        ("更新操作必须走 GET→改→POST集合端点，平台不支持直接PUT", "§2.2"),
        ("body字段传 dict 即可，由 platform_client 内部做一次 json.dumps，禁止调用方再序列化", "§2.3"),
        ("从JSON/API读入的ID做dict lookup前，必须统一转str：mapping.get(str(quote_id))", "§2.4"),
    ]

    def __init__(self):
        self.manifest: Dict[str, int] = {}
        self.common_cases: Dict[int, Dict] = {}
        self.config_rules: Dict = {}

    def load_knowledge(self):
        manifest_path = os.path.join(PROJECT_ROOT, "knowledge", "common_cases_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                self.manifest = json.load(f)

        common_dir = os.path.join(PROJECT_ROOT, "knowledge", "common_cases")
        if os.path.isdir(common_dir):
            for fname in os.listdir(common_dir):
                if not fname.endswith(".json"):
                    continue
                fpath = os.path.join(common_dir, fname)
                with open(fpath, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                cid = data.get("case_id")
                if cid:
                    self.common_cases[int(cid)] = data   # 统一用 int key（§2.4教训）

        rules_path = os.path.join(PROJECT_ROOT, "knowledge", "audit", "config_rules.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                self.config_rules = json.load(f)

    def align(self, dimensions: List[Dimension], actions: List[BusinessAction]) -> List[ApiAlignment]:
        results = []
        for dim in dimensions:
            alignment = ApiAlignment(dimension_name=dim.name)

            # 在 manifest 中搜索匹配的公共步骤
            matched = []
            for alias, cid in self.manifest.items():
                if dim.name in alias or any(v in alias for v in dim.values):
                    matched.append((alias, cid))
            if matched:
                best_alias, best_id = matched[0]
                alignment.matched_common_step = best_alias
                alignment.matched_case_id = int(best_id)
                detail = self.common_cases.get(int(best_id), {})
                alignment.required_inputs = [inp["name"] for inp in detail.get("inputs", [])]

            # 搜索 config_rules 中对应维度
            for rd in self.config_rules.get("dimensions", []):
                if rd["name"] == dim.name:
                    alignment.api_field = rd.get("name", "")
                    break

            alignment.type_traps = [f"{desc}（{src}）" for desc, src in self.TYPE_TRAP_RULES]
            results.append(alignment)

        return results

    def check_step_state_coverage(self, dimensions: List[Dimension]) -> Dict:
        mapping = self.config_rules.get("step_state_mapping", {})
        rule_dims = [d["name"] for d in self.config_rules.get("dimensions", [])]
        if not rule_dims:
            return {}

        covered_states: Set[Tuple] = set()
        for step_id, state in mapping.items():
            combo = tuple(str(state.get(rd, "?")) for rd in rule_dims)
            covered_states.add(combo)

        possible_values = [["True", "False"] for _ in rule_dims]
        all_combos: Set[Tuple] = set(itertools.product(*possible_values))
        missing = all_combos - covered_states

        return {
            "rule_dimensions": rule_dims,
            "total_combos": len(all_combos),
            "covered_combos": len(covered_states),
            "missing_combos": [dict(zip(rule_dims, m)) for m in missing],
            "existing_step_ids": list(mapping.keys()),
        }


# ─────────────────────────── Layer 4: DualVerifier ───────────────────────────

class DualVerifier:
    """将预期结果拆解为前端表现 + 后端真相"""

    FRONTEND_PATTERNS = [
        (r'显示(?:为|了|出)?', "UI_DISPLAY"),
        (r'提示(?:信息|消息|框)?', "UI_TOAST"),
        (r'页面.*(?:变|跳转|刷新)', "UI_NAVIGATION"),
        (r'列表.*(?:包含|显示|出现)', "UI_LIST"),
        (r'状态.*(?:切换|变为|更新为)', "UI_STATE_CHANGE"),
    ]

    BACKEND_PATTERNS = [
        (r'IP地址.*(?:分配|获取|自动)', "API_IP_ASSIGN"),
        (r'(?:能够|可以)?正常通信', "API_CONNECTIVITY"),
        (r'信号强度.*(?:值|数值|dBm)', "API_SIGNAL_METRIC"),
        (r'认证(?:成功|通过)', "API_AUTH_RESULT"),
        (r'认证(?:失败|拒绝)', "API_AUTH_REJECT"),
        (r'(?:日志|记录).*(?:显示|包含|存在)', "LOG_CHECK"),
        (r'(?:在线设备|在线列表).*(?:包含|不包含)', "API_ONLINE_DEVICE"),
        (r'实时更新|动态变化', "API_REALTIME"),
        (r'设备.*(?:IP|地址).*不再', "API_NO_IP"),
    ]

    def analyze(self, cases: List[ManualCase]) -> List[DualVerification]:
        results = []
        for case in cases:
            clauses = [c.strip() for c in re.split(r'[，,；;。]', case.expected_result) if c.strip()]
            frontend, backend = [], []
            for clause in clauses:
                matched_fe = any(re.search(p, clause) for p, _ in self.FRONTEND_PATTERNS)
                matched_be = any(re.search(p, clause) for p, _ in self.BACKEND_PATTERNS)
                if matched_be:
                    tag = next(t for p, t in self.BACKEND_PATTERNS if re.search(p, clause))
                    backend.append(f"[{tag}] {clause}")
                elif matched_fe:
                    tag = next(t for p, t in self.FRONTEND_PATTERNS if re.search(p, clause))
                    frontend.append(f"[{tag}] {clause}")
                else:
                    frontend.append(f"[UI_GENERAL] {clause}")

            results.append(DualVerification(
                case_id=case.case_id,
                raw_expected=case.expected_result,
                frontend_assertions=frontend,
                backend_assertions=backend,
                missing_backend=len(backend) == 0,
            ))
        return results


# ─────────────────────────── Layer 5: RiskTagger ───────────────────────────

class RiskTagger:
    """识别自动化风险与不可自动化动作"""

    # ═══ BLOCKER: 物理操作 ═══
    PHYSICAL_BLOCKERS = [
        (r'移动设备.*(?:远离|靠近|位移)',
         "需要物理位移设备，纯软件无法模拟",
         "替代方案：使用可编程射频衰减器模拟信号强度变化，或 mock API 返回值"),
        (r'拔插|拔出.*网线|插入.*网线',
         "涉及物理网线拔插",
         "替代方案：可编程交换机执行 switchport shutdown / no shutdown，或 SNMP 控制"),
        (r'重启(?:设备|系统|服务器|路由器|交换机)',
         "涉及设备重启（周期长且不可控）",
         "替代方案：通过带外管理接口（IPMI/iLO/BMC）或设备管理 API 触发重启"),
        (r'断电|掉电|关机|强制关机',
         "涉及物理断电操作",
         "替代方案：使用智能 PDU 远程控制电源"),
        (r'手动操作|人工(?:介入|干预|操作)',
         "明确标注需要人工介入",
         "替代方案：评估是否可通过 API / CLI 脚本完全替代人工步骤"),
        (r'扫描二维码|指纹|人脸识别|生物识别',
         "涉及生物识别或物理二维码扫描",
         "替代方案：使用 mock 服务返回预设的识别成功/失败结果"),
    ]

    # ═══ BLOCKER: 时间依赖（等待天级别 / 自然过期）═══
    TIMING_BLOCKERS = [
        (r'等待\s*\d+\s*天|经过\s*\d+\s*天|超过\s*\d+\s*天|\d+\s*个?自然日',
         "需要等待多天，CI/CD 中无法接受",
         "替代方案：通过 API 直接修改系统时间或数据库时间戳，快进到目标时间点"),
        (r'密码.*(?:超过|过了|超出).*有效期|密码.*过期|有效期.*(?:到期|届满)',
         "依赖密码有效期自然到期（可能需要数天/数月）",
         "替代方案：通过 API 将密码到期时间改为当前时间+1秒，立即触发过期逻辑"),
        (r'(?:证书|token|会话|session).*(?:自然)?(?:过期|失效|超时)',
         "依赖证书/Token 自然过期",
         "替代方案：通过 API 缩短有效期至最小值，或直接调用吊销/删除接口"),
        (r'\d+\s*个?(?:工作日|自然日)后|下一个工作日',
         "依赖工作日级别延迟",
         "替代方案：Mock 时间服务，或通过配置将时间窗口缩短至秒级"),
        (r'(?:下次|下一次).*(?:登录|上线|连接)',
         "依赖下次特定事件触发，时间不确定",
         "替代方案：手动触发登录/上线事件，或 mock 触发条件"),
    ]

    # ═══ HIGH: 高难度但有解法 ═══
    HIGH_RISK_PATTERNS = [
        (r'等待\s*\d+\s*(?:分钟|分|min)',
         "固定等待分钟级别，影响执行效率",
         "建议：使用轮询（poll_until）机制替代 sleep，设置合理超时上限"),
        (r'手动.*(?:刷新|重连|重试)',
         "依赖手动交互触发步骤",
         "建议：通过 API 调用或 WebDriver driver.refresh() 替代手动刷新"),
        (r'观察.*(?:变化|更新|动态)',
         "需要持续观察动态 UI 变化",
         "建议：使用 WebSocket 订阅或轮询 API 获取状态，加断言超时"),
        (r'不同.*(?:浏览器|终端|设备).*(?:同时|并发)',
         "涉及多终端/多浏览器并发",
         "建议：使用 pytest-xdist / Playwright 多 worker 并发运行"),
        (r'(?:信号|网络).*(?:抖动|不稳定|随机)',
         "依赖网络不稳定的随机行为",
         "建议：使用 tc netem 模拟网络抖动，或 mock 接口返回不稳定场景"),
    ]

    def tag(self, cases: List[ManualCase], actions: List[BusinessAction]) -> List[RiskItem]:
        risks: List[RiskItem] = []

        for case in cases:
            full_text = (
                f"{case.case_title} {case.precondition} "
                f"{' '.join(s.get('description', '') for s in case.steps)} "
                f"{case.expected_result}"
            )

            for pattern, desc, suggestion in self.PHYSICAL_BLOCKERS:
                if re.search(pattern, full_text, re.IGNORECASE):
                    risks.append(RiskItem(
                        case_id=case.case_id,
                        case_title=case.case_title,
                        risk_level="BLOCKER",
                        risk_type="PHYSICAL",
                        description=desc,
                        suggestion=suggestion,
                    ))

            for pattern, desc, suggestion in self.TIMING_BLOCKERS:
                if re.search(pattern, full_text, re.IGNORECASE):
                    risks.append(RiskItem(
                        case_id=case.case_id,
                        case_title=case.case_title,
                        risk_level="BLOCKER",
                        risk_type="TIMING",
                        description=desc,
                        suggestion=suggestion,
                    ))

            for pattern, desc, suggestion in self.HIGH_RISK_PATTERNS:
                if re.search(pattern, full_text, re.IGNORECASE):
                    risks.append(RiskItem(
                        case_id=case.case_id,
                        case_title=case.case_title,
                        risk_level="HIGH",
                        risk_type="ENVIRONMENT",
                        description=desc,
                        suggestion=suggestion,
                    ))

        # 不可参数化的业务动作 → 额外标注
        for action in actions:
            if not action.parameterizable:
                risks.append(RiskItem(
                    case_id=", ".join(action.case_ids),
                    case_title=action.name,
                    risk_level="BLOCKER",
                    risk_type="PHYSICAL" if "PHYSICAL" in action.intent_pattern else "TIMING",
                    description=f"业务动作「{action.name}」含不可自动化意图，无法参数化为公共步骤",
                    suggestion="需额外硬件控制层，或降级为手工测试用例",
                ))

        # 去重（同一 case_id 同一描述只保留一次）
        seen: Set[Tuple] = set()
        deduped = []
        for r in risks:
            key = (r.case_id, r.description)
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        return deduped


# ─────────────────────────── Report Generator ───────────────────────────

def _suggest_step_name(action: BusinessAction) -> str:
    if not action.parameterizable:
        return f"[手工/跳过] {action.name}"
    if action.data_injections:
        params = ", ".join(f"{{{d}}}" for d in action.data_injections[:2])
        return f"【公共】{action.name}（{params}）"
    return f"【公共】{action.name}"


class ReportGenerator:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_all(
        self,
        cases: List[ManualCase],
        actions: List[BusinessAction],
        dimensions: List[Dimension],
        gaps: List[CartesianGap],
        api_alignments: List[ApiAlignment],
        step_state_coverage: Dict,
        dual_vfs: List[DualVerification],
        risks: List[RiskItem],
    ) -> Dict[str, str]:
        files = {}

        md_path = os.path.join(self.output_dir, f"{self.ts}_case_design_analysis.md")
        self._write_markdown(md_path, cases, actions, dimensions, gaps,
                             api_alignments, step_state_coverage, dual_vfs, risks)
        files["markdown"] = md_path

        json_path = os.path.join(self.output_dir, "case_design_analysis.json")
        self._write_json(json_path, cases, actions, dimensions, gaps,
                         api_alignments, step_state_coverage, dual_vfs, risks)
        files["json"] = json_path

        csv_path = os.path.join(self.output_dir, "dimension_matrix.csv")
        self._write_csv(csv_path, dimensions, gaps)
        files["csv"] = csv_path

        catalog_path = os.path.join(self.output_dir, "reusable_steps_catalog.json")
        self._write_catalog(catalog_path, actions)
        files["catalog"] = catalog_path

        return files

    # ── Markdown ──────────────────────────────────────────────────────────────

    def _write_markdown(self, path, cases, actions, dimensions, gaps,
                        api_alignments, step_state_coverage, dual_vfs, risks):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blockers = [r for r in risks if r.risk_level == "BLOCKER"]
        highs = [r for r in risks if r.risk_level == "HIGH"]
        covered = sum(1 for g in gaps if g.covered)
        missing_be = sum(1 for v in dual_vfs if v.missing_backend)

        r = []
        r.append("# 用例设计分析报告 v2\n\n")
        r.append(f"> 生成时间: {now} | 用例: {len(cases)} | "
                 f"维度: {len(dimensions)} | 业务动作: {len(actions)} | "
                 f"不可自动化: {len(blockers)} | 缺后端验证: {missing_be}\n\n")
        r.append(f"---\n\n")

        # ── §1 业务动作聚类 ──
        r.append("## §1 业务动作聚类\n\n")
        r.append("> 碎片UI步骤 → 业务动作，每个业务动作对应一个公共步骤的粒度。\n\n")
        r.append("| 动作ID | 业务动作 | 意图链 | 覆盖用例 | 数据注入点 | 可自动化 |\n")
        r.append("|--------|---------|--------|---------|-----------|----------|\n")
        for a in actions:
            chain = "→".join(a.intent_pattern)
            data = ", ".join(a.data_injections[:2]) or "—"
            auto = "✅" if a.parameterizable else "🔴 **否**"
            r.append(f"| {a.action_id} | {a.name} | `{chain}` | "
                     f"{len(a.case_ids)} | {data} | {auto} |\n")
        r.append("\n")

        r.append("### 建议公共步骤清单\n\n")
        automatable = [a for a in actions if a.parameterizable]
        non_auto = [a for a in actions if not a.parameterizable]
        if automatable:
            r.append("**可建公共步骤**:\n\n")
            for a in automatable:
                r.append(f"- `{_suggest_step_name(a)}`\n")
                r.append(f"  - 原始步骤: {' → '.join(a.raw_steps[:3])}\n")
                if a.data_injections:
                    r.append(f"  - 参数化变量: `{'`, `'.join(a.data_injections)}`\n")
            r.append("\n")
        if non_auto:
            r.append("**🔴 不可建公共步骤（需人工/硬件介入）**:\n\n")
            for a in non_auto:
                r.append(f"- `{a.name}` — {', '.join(a.intent_pattern)}\n")
            r.append("\n")

        # ── §2 维度归纳 ──
        r.append("## §2 维度归纳\n\n")
        if dimensions:
            r.append("| 维度 | 类型 | 值域 | 对应API字段 |\n")
            r.append("|------|------|------|------------|\n")
            for d in dimensions:
                vals = " / ".join(d.values)
                r.append(f"| {d.name} | {d.dim_type} | {vals} | {d.api_field or '待确认'} |\n")
        else:
            r.append("> ⚠️ 未归纳出多值维度，建议在用例前置条件中明确写出关键参数。\n")
        r.append("\n")

        # ── §3 笛卡尔积缺口 ──
        r.append("## §3 笛卡尔积缺口\n\n")
        r.append("> **复盘§1.2**: 3个开关 → 2³=8种组合，只建3个公共步骤 → 37/80用例引用错误。\n\n")

        if gaps and "_summary" in gaps[0].combination:
            r.append(f"⚠️ {gaps[0].combination['_summary']}\n\n")
        else:
            total = len(gaps)
            missing_gaps = [g for g in gaps if not g.covered]
            r.append(f"**组合总数**: {total} | **已覆盖**: {covered} | "
                     f"**缺失**: {len(missing_gaps)}\n\n")
            if missing_gaps:
                r.append("### ⚠️ 缺失组合（每个缺口需新建一个公共步骤）\n\n")
                header_dims = list(missing_gaps[0].combination.keys())
                r.append("| " + " | ".join(header_dims) + " |\n")
                r.append("| " + " | ".join(["---"] * len(header_dims)) + " |\n")
                for g in missing_gaps:
                    r.append("| " + " | ".join(g.combination.values()) + " |\n")
                r.append("\n")
            else:
                r.append("✅ 所有维度组合均有对应用例覆盖\n\n")

        # ── §4 API对齐 ──
        r.append("## §4 API对齐 + 类型陷阱\n\n")

        has_any_match = any(a.matched_common_step for a in api_alignments)
        if api_alignments:
            r.append("### 维度 → 公共步骤匹配\n\n")
            r.append("| 维度 | 匹配公共步骤 | 步骤ID | 必需入参 |\n")
            r.append("|------|------------|--------|--------|\n")
            for a in api_alignments:
                step_name = a.matched_common_step or "❌ 无匹配，需新建"
                step_id = str(a.matched_case_id) if a.matched_case_id else "—"
                inputs = ", ".join(a.required_inputs[:4]) or "—"
                r.append(f"| {a.dimension_name} | {step_name} | {step_id} | {inputs} |\n")
            r.append("\n")

        if step_state_coverage and step_state_coverage.get("rule_dimensions"):
            ssc = step_state_coverage
            r.append("### config_rules 状态覆盖\n\n")
            r.append(f"- 规则维度: {', '.join(ssc['rule_dimensions'])}\n")
            r.append(f"- 应有组合: {ssc['total_combos']} | 已有: {ssc['covered_combos']} "
                     f"（步骤: {', '.join(ssc['existing_step_ids'])}）\n")
            if ssc["missing_combos"]:
                r.append(f"- ⚠️ **缺失组合 {len(ssc['missing_combos'])} 个**:\n")
                for mc in ssc["missing_combos"]:
                    r.append(f"  - {mc}\n")
            r.append("\n")

        r.append("### 🔴 类型陷阱（来自复盘）\n\n")
        r.append("| # | 陷阱 | 来源 |\n")
        r.append("|---|------|------|\n")
        for i, (desc, src) in enumerate(ApiAligner.TYPE_TRAP_RULES, 1):
            r.append(f"| {i} | {desc} | {src} |\n")
        r.append("\n")

        # ── §5 双重验证 ──
        r.append("## §5 双重验证方案\n\n")
        r.append("> 每条用例的「预期结果」分解为: **前端表现**（UI断言）+ **后端真相**（API/Log断言）\n")
        r.append(f"> 缺少后端验证的用例: **{missing_be}/{len(dual_vfs)}**\n\n")

        r.append("| 用例ID | 前端表现 | 后端真相 | 缺后端 |\n")
        r.append("|--------|---------|---------|-------|\n")
        for v in dual_vfs:
            fe = "; ".join(v.frontend_assertions[:2]) or "—"
            be = "; ".join(v.backend_assertions[:2]) or "—"
            miss = "🔴 **是**" if v.missing_backend else "✅"
            r.append(f"| {v.case_id} | {fe[:55]} | {be[:55]} | {miss} |\n")
        r.append("\n")

        if missing_be > 0:
            r.append("### 缺少后端验证的用例，建议补充以下断言类型:\n\n")
            r.append("- `API_AUTH_RESULT` — 调用 GET /auth/status 断言认证状态\n")
            r.append("- `API_ONLINE_DEVICE` — 调用 GET /device/online 断言设备在线列表\n")
            r.append("- `LOG_CHECK` — 查询日志接口，断言日志中含关键字\n\n")

        # ── §6 风险清单 ──
        r.append("## §6 风险与不可自动化标注\n\n")

        if blockers:
            r.append(f"### 🔴 BLOCKER — 不可自动化 / 成本极高（{len(blockers)}项）\n\n")
            r.append("| 用例ID | 类型 | 风险描述 | 替代/解决方案 |\n")
            r.append("|--------|------|---------|-------------|\n")
            for ri in blockers:
                r.append(f"| {ri.case_id} | {ri.risk_type} | "
                         f"{ri.description} | {ri.suggestion} |\n")
            r.append("\n")

        if highs:
            r.append(f"### 🟡 HIGH — 难度高但有解法（{len(highs)}项）\n\n")
            r.append("| 用例ID | 类型 | 风险描述 | 建议 |\n")
            r.append("|--------|------|---------|------|\n")
            for ri in highs:
                r.append(f"| {ri.case_id} | {ri.risk_type} | "
                         f"{ri.description} | {ri.suggestion} |\n")
            r.append("\n")

        if not blockers and not highs:
            r.append("✅ 未发现不可自动化风险\n\n")

        # ── §7 复盘防护 ──
        r.append("## §7 复盘防护检查\n\n")
        r.append("> 逐条对应 `knowledge/case_design/insight.md` 的血泪教训\n\n")
        uncovered_cnt = sum(1 for g in gaps if not g.covered and "_summary" not in g.combination)
        checks = [
            ("Phase 0 先输出状态组合映射表再动手", "§1.1", f"✅ §3已输出笛卡尔积矩阵，缺口{uncovered_cnt}个"),
            ("公共步骤颗粒度 = 独立维度全排列", "§1.2", f"✅ {len(dimensions)}个维度，全排列已计算"),
            ("先单条验证API参数再批量", "§1.3", "⚠️ 请在执行前手工验证一条 create_step"),
            ("审计前置，非事后补救", "§1.4", "✅ 本报告即 Phase 0 前置分析"),
            ("method 字段传 int(0/1/2/3)", "§2.1", "✅ §4类型陷阱已列出"),
            ("更新走 GET→改→POST", "§2.2", "✅ §4类型陷阱已列出"),
            ("body 不要双重序列化", "§2.3", "✅ §4类型陷阱已列出"),
            ("dict key int/str 一致", "§2.4", "✅ §4类型陷阱已列出"),
            ("公共步骤 body 从模板派生", "§2.6", "⚠️ 请从已验证用例 GET 原始 body 后派生"),
        ]
        r.append("| # | 检查项 | 来源 | 本报告覆盖情况 |\n")
        r.append("|---|--------|------|---------------|\n")
        for i, (check, src, cover) in enumerate(checks, 1):
            r.append(f"| {i} | {check} | {src} | {cover} |\n")
        r.append("\n")

        # ── §8 实施路线图 ──
        r.append("## §8 实施路线图\n\n")
        r.append(f"**Phase 1 — 补齐公共步骤** ({uncovered_cnt} 个缺口)\n")
        r.append("1. 从已验证 body 模板派生各缺口的 HTTP body\n")
        r.append("2. 单条 create_step API 验证参数正确性\n")
        r.append("3. 批量创建全部缺失公共步骤\n\n")
        r.append("**Phase 2 — 样本创建+审计**\n")
        r.append("1. 每种组合创建 1 条样本业务用例\n")
        r.append("2. 用 case-debugger 审计：CONFIG_MISMATCH = 0 才继续\n\n")
        r.append("**Phase 3 — 批量+全量审计**\n")
        r.append("1. 批量创建剩余业务用例\n")
        r.append("2. 全量审计，所有偏差类型均为 0\n")
        r.append("3. 同步 case_id 到飞书，更新知识库 manifest\n\n")

        if blockers:
            blocker_ids = ", ".join(set(ri.case_id for ri in blockers))
            r.append(f"**⚠️ 需手工处理的用例**: {blocker_ids}\n")
            r.append("以上 BLOCKER 用例需另行制定手工测试计划或硬件环境方案。\n")

        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(r))

    # ── JSON ──────────────────────────────────────────────────────────────────

    def _write_json(self, path, cases, actions, dimensions, gaps,
                    api_alignments, step_state_coverage, dual_vfs, risks):
        report = {
            "metadata": {
                "version": "2.0",
                "analysis_time": datetime.now().isoformat(),
                "total_cases": len(cases),
                "insight_ref": "knowledge/case_design/insight.md",
            },
            "business_actions": [
                {
                    "action_id": a.action_id,
                    "name": a.name,
                    "intent_pattern": list(a.intent_pattern),
                    "case_ids": a.case_ids,
                    "data_injections": a.data_injections,
                    "parameterizable": a.parameterizable,
                    "suggested_step_name": _suggest_step_name(a),
                }
                for a in actions
            ],
            "dimensions": [
                {"name": d.name, "type": d.dim_type, "values": d.values}
                for d in dimensions
            ],
            "cartesian_gaps": {
                "total": len(gaps),
                "covered": sum(1 for g in gaps if g.covered),
                "missing": [g.combination for g in gaps if not g.covered],
            },
            "api_alignment": [
                {
                    "dimension": a.dimension_name,
                    "matched_step": a.matched_common_step,
                    "matched_id": a.matched_case_id,
                    "required_inputs": a.required_inputs,
                }
                for a in api_alignments
            ],
            "step_state_coverage": step_state_coverage,
            "dual_verification": [
                {
                    "case_id": v.case_id,
                    "frontend": v.frontend_assertions,
                    "backend": v.backend_assertions,
                    "missing_backend": v.missing_backend,
                }
                for v in dual_vfs
            ],
            "risks": [
                {
                    "case_id": ri.case_id,
                    "level": ri.risk_level,
                    "type": ri.risk_type,
                    "description": ri.description,
                    "suggestion": ri.suggestion,
                }
                for ri in risks
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    # ── CSV ───────────────────────────────────────────────────────────────────

    def _write_csv(self, path, dimensions, gaps):
        lines = []
        if not dimensions:
            lines.append("（无维度）\n")
        elif gaps and "_summary" in gaps[0].combination:
            lines.append(f"SUMMARY,{gaps[0].combination['_summary']}\n")
        else:
            dim_names = [d.name for d in dimensions]
            lines.append(",".join(["编号"] + dim_names + ["状态", "匹配用例"]) + "\n")
            for i, g in enumerate(gaps, 1):
                vals = [g.combination.get(dn, "*") for dn in dim_names]
                status = "已覆盖" if g.covered else "缺失"
                lines.append(",".join([str(i)] + vals + [status, g.matched_case_id]) + "\n")
        with open(path, "w", encoding="utf-8-sig") as f:
            f.writelines(lines)

    # ── Catalog ───────────────────────────────────────────────────────────────

    def _write_catalog(self, path, actions):
        catalog = {
            "automatable_actions": [],
            "non_automatable_actions": [],
        }
        for a in actions:
            entry = {
                "action_id": a.action_id,
                "name": a.name,
                "intent_pattern": list(a.intent_pattern),
                "case_count": len(a.case_ids),
                "suggested_step_name": _suggest_step_name(a),
                "data_injections": a.data_injections,
            }
            if a.parameterizable:
                catalog["automatable_actions"].append(entry)
            else:
                catalog["non_automatable_actions"].append(entry)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)


# ─────────────────────────── Orchestrator ───────────────────────────

class CaseDesignAnalyzer:
    """v2 分析器 — 5层管线编排"""

    def __init__(self):
        self.cases: List[ManualCase] = []
        self.output_dir = ""
        self.actions: List[BusinessAction] = []
        self.dimensions: List[Dimension] = []
        self.gaps: List[CartesianGap] = []
        self.api_alignments: List[ApiAlignment] = []
        self.step_state_coverage: Dict = {}
        self.dual_verifications: List[DualVerification] = []
        self.risks: List[RiskItem] = []

    def load_cases(self, input_file: str) -> bool:
        try:
            with open(input_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            if not isinstance(data, list):
                print("❌ 输入格式错误，期望JSON数组")
                return False
            self.cases = [ManualCase(**c) for c in data]
            print(f"✅ 加载 {len(self.cases)} 条用例")
            return True
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False

    def analyze(self) -> bool:
        if not self.cases:
            print("❌ 无用例数据")
            return False

        print("\n🔬 5层分析管线启动...\n")

        print("  [1/5] Layer 1: 业务动作聚类...")
        self.actions = BusinessClusterer().cluster(self.cases)
        print(f"         → {len(self.actions)} 个业务动作，"
              f"{sum(1 for a in self.actions if not a.parameterizable)} 个不可自动化")

        print("  [2/5] Layer 2: 维度归纳 + 笛卡尔积缺口...")
        self.dimensions, self.gaps = DimensionMiner().mine(self.cases)
        covered = sum(1 for g in self.gaps if g.covered)
        print(f"         → {len(self.dimensions)} 个维度, "
              f"{len(self.gaps)} 种组合 (覆盖 {covered})")

        print("  [3/5] Layer 3: API对齐 + 知识库匹配...")
        aligner = ApiAligner()
        aligner.load_knowledge()
        self.api_alignments = aligner.align(self.dimensions, self.actions)
        self.step_state_coverage = aligner.check_step_state_coverage(self.dimensions)
        print(f"         → 知识库 {len(aligner.manifest)} 个公共步骤")

        print("  [4/5] Layer 4: 双重验证拆解...")
        self.dual_verifications = DualVerifier().analyze(self.cases)
        missing_be = sum(1 for v in self.dual_verifications if v.missing_backend)
        print(f"         → {missing_be}/{len(self.dual_verifications)} 条缺少后端验证")

        print("  [5/5] Layer 5: 风险感知 + 不可自动化标注...")
        self.risks = RiskTagger().tag(self.cases, self.actions)
        blockers = sum(1 for r in self.risks if r.risk_level == "BLOCKER")
        highs = sum(1 for r in self.risks if r.risk_level == "HIGH")
        print(f"         → 🔴 BLOCKER={blockers}  🟡 HIGH={highs}")

        print("\n✅ 分析完成\n")
        return True

    def generate_reports(self, output_dir: str = None) -> bool:
        if not output_dir:
            output_dir = os.path.join(PROJECT_ROOT, "workspace", "analysis", "case_design_reports")
        self.output_dir = output_dir
        try:
            gen = ReportGenerator(output_dir)
            files = gen.generate_all(
                self.cases, self.actions, self.dimensions, self.gaps,
                self.api_alignments, self.step_state_coverage,
                self.dual_verifications, self.risks,
            )
            for name, path in files.items():
                print(f"  ✅ {name}: {path}")
            return True
        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
            import traceback; traceback.print_exc()
            return False

    def print_summary(self):
        blockers = [r for r in self.risks if r.risk_level == "BLOCKER"]
        highs = [r for r in self.risks if r.risk_level == "HIGH"]
        covered = sum(1 for g in self.gaps if g.covered)
        missing_be = sum(1 for v in self.dual_verifications if v.missing_backend)

        print("\n" + "=" * 70)
        print("📊 Case Design Analyzer v2 — 分析摘要")
        print("=" * 70)
        print(f"  用例总数      : {len(self.cases)}")
        print(f"  业务动作      : {len(self.actions)} 个")
        print(f"  识别维度      : {len(self.dimensions)} 个")
        print(f"  笛卡尔积覆盖  : {covered}/{len(self.gaps)}")
        print(f"  缺后端验证    : {missing_be}/{len(self.dual_verifications)} 条")
        print(f"  风险项        : 🔴 BLOCKER={len(blockers)}  🟡 HIGH={len(highs)}")
        print("=" * 70)

        if blockers:
            print("\n🔴 不可自动化 / 高成本用例:")
            for ri in blockers:
                print(f"  [{ri.risk_type}] {ri.case_id} — {ri.description}")
                print(f"          ↳ {ri.suggestion}")

        uncovered = [g for g in self.gaps
                     if not g.covered and "_summary" not in g.combination]
        if uncovered:
            print(f"\n⚠️ 笛卡尔积缺口 ({len(uncovered)} 个):")
            for g in uncovered[:5]:
                combo = ", ".join(f"{k}={v}" for k, v in g.combination.items())
                print(f"  ❌ {combo}")
            if len(uncovered) > 5:
                print(f"  ... 还有 {len(uncovered) - 5} 个，见报告 §3")

        print()


# ─────────────────────────── Main ───────────────────────────

def main():
    print("🚀 Case Design Analyzer v2\n")
    input_file = os.path.join(PROJECT_ROOT, "workspace", "analysis", "manual_cases.json")
    if not os.path.exists(input_file):
        print(f"⚠️  输入文件不存在: {input_file}")
        print("请在 workspace/analysis/ 下放置 manual_cases.json")
        return False

    analyzer = CaseDesignAnalyzer()
    if not analyzer.load_cases(input_file):
        return False
    if not analyzer.analyze():
        return False
    if not analyzer.generate_reports():
        return False
    analyzer.print_summary()
    print(f"✨ 报告: {analyzer.output_dir}")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
