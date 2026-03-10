#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用例调试器 (Case Debugger)
自动化用例质量审计与偏差修复。

使用方式:
    from case_debugger import CaseDebugger
    debugger = CaseDebugger(business_dir_id=67136, common_dir_id=66880)
    report = debugger.run_full_audit()
    print(report.to_markdown())
"""

import sys
import os
import re
import json
import time
from datetime import datetime

# 确保能找到项目根目录的依赖
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'skills', 'sdet-skills', 'platform-client'))
sys.path.insert(0, PROJECT_ROOT)

from platform_client import PlatformClient
from config import Config


# ─────────────────────────── 数据类 ───────────────────────────

class StepInfo:
    """单个步骤的结构化信息"""
    def __init__(self, order, step_type, step_id=None, name="", quote_id=None, quote_name="", category=""):
        self.order = order
        self.step_type = step_type  # "quote" | "http"
        self.step_id = step_id
        self.name = name
        self.quote_id = quote_id
        self.quote_name = quote_name
        self.category = category    # 配置/开户/认证/校验/清理/未知

    def to_dict(self):
        return {
            "order": self.order,
            "type": self.step_type,
            "step_id": self.step_id,
            "name": self.name,
            "quote_id": self.quote_id,
            "quote_name": self.quote_name,
            "category": self.category
        }


class CaseAnalysis:
    """单条业务用例的分析结果"""
    def __init__(self, case_id, case_name):
        self.case_id = case_id
        self.case_name = case_name
        self.steps = []          # List[StepInfo]
        self.variables = {}      # name -> value
        self.raw_data = None     # 平台原始数据

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables,
        }


class Deviation:
    """偏差条目"""
    STEP_MISSING = "STEP_MISSING"
    STEP_EXTRA = "STEP_EXTRA"
    ORDER_WRONG = "ORDER_WRONG"
    VAR_MISSING = "VAR_MISSING"
    COMMON_MISSING = "COMMON_MISSING"
    QUOTE_WRONG = "QUOTE_WRONG"
    CONFIG_MISMATCH = "CONFIG_MISMATCH"

    def __init__(self, dev_type, detail, severity="HIGH"):
        self.type = dev_type
        self.detail = detail
        self.severity = severity  # HIGH / MEDIUM / LOW

    def to_dict(self):
        return {"type": self.type, "detail": self.detail, "severity": self.severity}


class CaseDeviation:
    """单条用例的偏差集合"""
    def __init__(self, case_id, case_name):
        self.case_id = case_id
        self.case_name = case_name
        self.issues = []  # List[Deviation]

    @property
    def has_issues(self):
        return len(self.issues) > 0

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "issues": [i.to_dict() for i in self.issues]
        }


class AuditReport:
    """完整审计报告"""
    def __init__(self):
        self.business_cases = []       # List[CaseAnalysis]
        self.common_cases = []         # List[dict]  平台公共用例
        self.deviations = []           # List[CaseDeviation]
        self.missing_commons = []      # List[dict]  需要新增的公共用例建议
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    @property
    def total_cases(self):
        return len(self.business_cases)

    @property
    def deviated_cases(self):
        return [d for d in self.deviations if d.has_issues]

    @property
    def normal_count(self):
        return self.total_cases - len(self.deviated_cases)

    def to_markdown(self):
        lines = []
        lines.append(f"# 用例调试报告")
        lines.append(f"生成时间: {self.timestamp}\n")

        # 概览
        lines.append("## 概览")
        lines.append(f"- 业务用例总数: {self.total_cases}")
        lines.append(f"- 正常用例: {self.normal_count}")
        lines.append(f"- 偏差用例: {len(self.deviated_cases)}")
        lines.append(f"- 公共用例缺口: {len(self.missing_commons)}\n")

        # 公共用例缺口
        if self.missing_commons:
            lines.append("## 公共用例缺口")
            lines.append("| 编号 | 建议名称 | 说明 | 引用场景 |")
            lines.append("|------|---------|------|---------|")
            for idx, mc in enumerate(self.missing_commons, 1):
                refs = ", ".join(mc.get("referenced_by", [])[:5])
                lines.append(f"| {idx} | {mc['suggested_name']} | {mc.get('description', '')} | {refs} |")
            lines.append("")

        # 偏差用例明细
        if self.deviated_cases:
            lines.append("## 偏差用例明细")
            for dev in self.deviated_cases:
                lines.append(f"\n### {dev.case_name} (ID: {dev.case_id})")
                for issue in dev.issues:
                    icon = "❌" if issue.severity == "HIGH" else "⚠️" if issue.severity == "MEDIUM" else "ℹ️"
                    lines.append(f"- {icon} **{issue.type}**: {issue.detail} [{issue.severity}]")

        # 正常用例列表
        if self.normal_count > 0:
            lines.append("\n## 正常用例")
            normal_ids = set(a.case_id for a in self.business_cases) - set(d.case_id for d in self.deviated_cases)
            for analysis in self.business_cases:
                if analysis.case_id in normal_ids:
                    lines.append(f"- ✅ {analysis.case_name} (ID: {analysis.case_id})")

        return "\n".join(lines)

    def to_json(self):
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total": self.total_cases,
                "normal": self.normal_count,
                "deviated": len(self.deviated_cases),
                "missing_commons": len(self.missing_commons)
            },
            "missing_commons": self.missing_commons,
            "deviations": [d.to_dict() for d in self.deviated_cases],
            "all_analyses": [a.to_dict() for a in self.business_cases]
        }


# ─────────────────────────── 分类引擎 ───────────────────────────

# 默认的步骤分类规则（正则匹配公共用例名称 → 归属阶段）
DEFAULT_CATEGORY_RULES = [
    ("配置", re.compile(r"配置|修改.*管理|开启.*管控|关闭.*管控|策略|密码.*安全", re.IGNORECASE)),
    ("设备", re.compile(r"设备|创建设备|NAS", re.IGNORECASE)),
    ("开户", re.compile(r"开户|创建.*用户|新增.*用户|注册", re.IGNORECASE)),
    ("认证", re.compile(r"认证|1[Xx]|EAP|PEAP|PAP|CHAP|dot1x|portal|RADIUS认证|MAC认证", re.IGNORECASE)),
    ("记账", re.compile(r"记账|Acct|accounting", re.IGNORECASE)),
    ("查询", re.compile(r"查询|检查|校验|验证|获取.*信息", re.IGNORECASE)),
    ("清理", re.compile(r"删除|销户|恢复|清理|移除|下线", re.IGNORECASE)),
]


def classify_step(step_name):
    """根据步骤名称推断所属阶段"""
    for category, pattern in DEFAULT_CATEGORY_RULES:
        if pattern.search(step_name):
            return category
    return "未知"


# ─────────────────────────── 主类 ───────────────────────────

class CaseDebugger:
    """用例调试器主类"""

    def __init__(self, business_dir_id, common_dir_id,
                 state_template=None, config_rules=None,
                 manifest_path=None, dry_run=True):
        """
        Args:
            business_dir_id: 业务用例所在目录ID
            common_dir_id:   公共用例所在目录ID
            state_template:  期望状态机模板（可选）
            config_rules:    配置状态规则（dict），用于标题-配置步骤一致性审计
            manifest_path:   知识库manifest路径（默认读Config）
            dry_run:         仅分析不修改（默认True）
        """
        self.business_dir_id = business_dir_id
        self.common_dir_id = common_dir_id
        self.state_template = state_template
        self.config_rules = config_rules
        self.dry_run = dry_run
        self.manifest_path = manifest_path or Config.MANIFEST_PATH

        self.client = PlatformClient(
            base_url=Config.TEST_PLATFORM_URL,
            token=Config.TEST_PLATFORM_TOKEN,
            creator_name=Config.CREATOR_NAME,
            creator_id=str(Config.CREATOR_ID)
        )

        self._manifest = None
        self._manifest_reverse = None  # id -> alias
        self._verified_case_cache = {}  # id -> name (已在平台验证存在的用例缓存)

    # ─────── Phase 1: 数据采集 ───────

    def load_manifest(self):
        """加载知识库 manifest"""
        if self._manifest is None:
            try:
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    self._manifest = json.load(f)
            except FileNotFoundError:
                self._manifest = {}
            self._manifest_reverse = {v: k for k, v in self._manifest.items()}
        return self._manifest

    def _verify_case_exists(self, case_id):
        """
        在平台上验证用例是否真实存在（带缓存）。
        用于处理不在指定公共目录/知识库中但确实存在的全局公共用例。
        
        Returns:
            str or None: 用例名称（存在时），None（不存在时）
        """
        if case_id in self._verified_case_cache:
            return self._verified_case_cache[case_id]
        
        result = self.client.get_case(case_id)
        if result.get("success") and result.get("data"):
            name = result["data"].get("name", f"ID:{case_id}")
            self._verified_case_cache[case_id] = name
            return name
        
        self._verified_case_cache[case_id] = None
        return None

    def _get_alias_by_id(self, case_id):
        """通过ID反查知识库别名"""
        self.load_manifest()
        return self._manifest_reverse.get(case_id, None)

    def fetch_directory_cases(self, dir_id):
        """
        获取目录下所有用例（使用 get_cases_children，递归子目录）
        
        Returns:
            list[dict]: 平台用例数据列表
        """
        result = self.client.get_cases_children(dir_id)
        if not result.get("success"):
            print(f"[WARN] get_cases_children({dir_id}) 失败: {result.get('message')}")
            return []

        cases = []
        for item in result.get("data", []):
            case_type = item.get("caseType", -1)
            if case_type == 0:
                # 子目录 → 递归
                sub_cases = self.fetch_directory_cases(item["id"])
                cases.extend(sub_cases)
            else:
                # 用例
                cases.append(item)
        return cases

    def fetch_business_cases(self):
        """拉取业务用例目录下所有用例（含步骤和变量）"""
        raw_cases = self.fetch_directory_cases(self.business_dir_id)
        print(f"[Phase 1] 获取到 {len(raw_cases)} 条业务用例")
        return raw_cases

    def fetch_common_cases(self):
        """拉取公共用例目录下所有公共用例"""
        raw_cases = self.fetch_directory_cases(self.common_dir_id)
        print(f"[Phase 1] 获取到 {len(raw_cases)} 条公共用例")
        return raw_cases

    def _fetch_steps(self, case_id):
        """获取用例的步骤列表"""
        result = self.client.list_steps(case_id)
        if result.get("success"):
            return result.get("data", [])
        return []

    def _fetch_variables(self, case_id):
        """获取用例的变量列表"""
        result = self.client.get_case_variables_v2(case_id)
        if isinstance(result, dict) and result.get("success"):
            return result.get("data", [])
        return []

    # ─────── 配置状态解析 ───────

    def _parse_title_config_state(self, title):
        """
        根据 config_rules 从用例标题中解析期望的配置状态。

        Returns:
            dict: {dimension_name: True/False/None} 或空 dict（无规则时）
        """
        if not self.config_rules:
            return {}

        state = {}
        for dim in self.config_rules.get("dimensions", []):
            name = dim["name"]
            on_pat = re.compile(dim["on_pattern"])
            off_pat = re.compile(dim["off_pattern"])
            found_on = bool(on_pat.search(title))
            found_off = bool(off_pat.search(title))
            if found_on and not found_off:
                state[name] = True
            elif found_off and not found_on:
                state[name] = False
            else:
                state[name] = None  # 无法判断或矛盾
        return state

    def _get_config_step_state(self, step):
        """
        根据 config_rules 映射，查询某个引用步骤对应的配置状态。

        Returns:
            dict or None: {dimension_name: True/False} 或 None（未匹配）
        """
        if not self.config_rules or not step.quote_id:
            return None
        mapping = self.config_rules.get("step_state_mapping", {})
        return mapping.get(str(step.quote_id))

    def _find_setup_config_step(self, steps):
        """
        在步骤列表中找到前置配置步骤（排除末尾清理步骤）。
        规则：找到含"配置"或"管控"或"校验控制"的引用步骤，
        且不是最后一个同类步骤（末尾的是清理步骤）。

        Returns:
            StepInfo or None
        """
        config_steps = []
        for s in steps:
            if s.step_type == "quote" and s.quote_name:
                if re.search(r"公共配置|管控|校验控制|密码.*安全.*管理", s.quote_name):
                    config_steps.append(s)

        if not config_steps:
            return None

        # 取第一个配置步骤（前置环境配置），最后一个通常是清理/恢复
        if len(config_steps) >= 2:
            return config_steps[0]
        # 只有一个时，判断位置：如果在前半部分则为配置步骤
        if config_steps[0].order <= len(steps) / 2:
            return config_steps[0]
        return None

    # ─────── Phase 2: 解析状态机 ───────

    def analyze_cases(self, raw_business_cases=None, raw_common_cases=None):
        """
        实际分析：逐条获取步骤和变量，构建状态机。

        Returns:
            list[CaseAnalysis]
        """
        if raw_business_cases is None:
            raw_business_cases = self.fetch_business_cases()
        if raw_common_cases is None:
            raw_common_cases = self.fetch_common_cases()

        # 建立公共用例 ID->名称 映射
        common_id_map = {}
        for c in raw_common_cases:
            common_id_map[c["id"]] = c.get("name", f"ID:{c['id']}")

        # 补充知识库映射
        manifest = self.load_manifest()
        for alias, cid in manifest.items():
            if cid not in common_id_map:
                common_id_map[cid] = alias

        analyses = []
        total = len(raw_business_cases)
        for idx, bc in enumerate(raw_business_cases):
            cid = bc["id"]
            cname = bc.get("name", f"ID:{cid}")
            print(f"\r[Phase 2] 分析 {idx+1}/{total}: {cname[:40]}...", end="", flush=True)

            analysis = CaseAnalysis(cid, cname)
            analysis.raw_data = bc

            # 获取步骤
            steps_raw = self._fetch_steps(cid)
            for s in steps_raw:
                step_type_val = s.get("type", 0)
                quote_id = s.get("quoteId")
                quote_name = ""
                category = "未知"

                if quote_id:
                    # 引用步骤 - 先查本地映射，查不到则去平台验证
                    qid_int = int(quote_id)
                    quote_name = common_id_map.get(qid_int)
                    if not quote_name:
                        # 本地未知，去平台实时查询
                        verified = self._verify_case_exists(qid_int)
                        quote_name = verified if verified else f"未知公共用例({quote_id})"
                    category = classify_step(quote_name)
                    si = StepInfo(
                        order=s.get("order", 0),
                        step_type="quote",
                        step_id=s.get("id"),
                        name=s.get("name", quote_name),
                        quote_id=int(quote_id),
                        quote_name=quote_name,
                        category=category
                    )
                else:
                    # 原生 HTTP 步骤
                    name = s.get("name", "未命名步骤")
                    category = classify_step(name)
                    si = StepInfo(
                        order=s.get("order", 0),
                        step_type="http",
                        step_id=s.get("id"),
                        name=name,
                        category=category
                    )
                analysis.steps.append(si)

            # 按 order 排序
            analysis.steps.sort(key=lambda x: x.order)

            # 获取变量
            vars_raw = self._fetch_variables(cid)
            for v in vars_raw:
                analysis.variables[v.get("name", "")] = v.get("value", "")

            analyses.append(analysis)

        print()  # 换行
        print(f"[Phase 2] 完成 {len(analyses)} 条用例的状态机分析")
        return analyses

    # ─────── Phase 3: 偏差检测 ───────

    def detect_deviations(self, analyses, common_cases_raw=None):
        """
        基于状态机模板检测偏差。

        Args:
            analyses: analyze_cases() 的结果
            common_cases_raw: 公共用例列表（可选，不传则重新拉取）

        Returns:
            list[CaseDeviation]
        """
        if common_cases_raw is None:
            common_cases_raw = self.fetch_common_cases()

        common_ids = set(c["id"] for c in common_cases_raw)
        manifest = self.load_manifest()
        all_known_common_ids = set(manifest.values()) | common_ids

        deviations = []
        missing_common_tracker = {}  # quote_id -> set(case_names)

        for analysis in analyses:
            cd = CaseDeviation(analysis.case_id, analysis.case_name)

            # 检测1: 引用的公共用例是否存在于公共目录或知识库
            for step in analysis.steps:
                if step.step_type == "quote" and step.quote_id:
                    if step.quote_id not in all_known_common_ids:
                        # 不在本地已知范围内，去平台验证是否真实存在
                        verified_name = self._verify_case_exists(step.quote_id)
                        if verified_name:
                            # 平台确认存在（全局公共用例），补充名称，不报错
                            if not step.quote_name or step.quote_name.startswith("未知"):
                                step.quote_name = verified_name
                                step.category = classify_step(verified_name)
                        else:
                            cd.issues.append(Deviation(
                                Deviation.QUOTE_WRONG,
                                f"步骤{step.order}引用了用例ID={step.quote_id}，在平台上不存在",
                                "HIGH"
                            ))

            # 检测2: 如果有状态机模板，检查必要阶段
            if self.state_template:
                step_categories = [s.category for s in analysis.steps]
                for phase_def in self.state_template.get("expected_phases", []):
                    phase_name = phase_def["phase"]
                    required = phase_def.get("required", False)
                    pattern = phase_def.get("common_pattern", "")

                    # 检查是否有步骤匹配该阶段
                    phase_found = phase_name in step_categories
                    if not phase_found and pattern:
                        # 用正则再搜一遍步骤名称
                        pat = re.compile(pattern, re.IGNORECASE)
                        phase_found = any(pat.search(s.name) or pat.search(s.quote_name) for s in analysis.steps)

                    if required and not phase_found:
                        cd.issues.append(Deviation(
                            Deviation.STEP_MISSING,
                            f"缺少必要阶段「{phase_name}」(模板要求: {pattern})",
                            "HIGH"
                        ))

            # 检测3: 引用步骤需要的变量是否已注入
            for step in analysis.steps:
                if step.step_type == "quote" and step.quote_id:
                    # 从知识库查找该公共用例需要的 inputs
                    alias = self._get_alias_by_id(step.quote_id)
                    if alias:
                        case_json_path = os.path.join(Config.COMMON_CASES_DIR, f"{alias}.json")
                        if os.path.exists(case_json_path):
                            with open(case_json_path, 'r', encoding='utf-8') as f:
                                common_detail = json.load(f)
                            for inp in common_detail.get("inputs", []):
                                var_name = inp.get("name", "")
                                if var_name and var_name not in analysis.variables:
                                    cd.issues.append(Deviation(
                                        Deviation.VAR_MISSING,
                                        f"步骤{step.order}引用「{alias}」需要变量 {var_name}，但业务用例未注入",
                                        "MEDIUM"
                                    ))

            # 检测4: 标题-配置步骤一致性
            if self.config_rules:
                title_state = self._parse_title_config_state(analysis.case_name)
                if any(v is not None for v in title_state.values()):
                    setup_step = self._find_setup_config_step(analysis.steps)
                    if setup_step:
                        step_state = self._get_config_step_state(setup_step)
                        if step_state is not None:
                            mismatches = []
                            for dim_name, expected in title_state.items():
                                if expected is None:
                                    continue
                                actual = step_state.get(dim_name)
                                if actual is not None and actual != expected:
                                    exp_str = "开启" if expected else "关闭"
                                    act_str = "开启" if actual else "关闭"
                                    mismatches.append(f"{dim_name}(期望:{exp_str}, 实际:{act_str})")
                            if mismatches:
                                cd.issues.append(Deviation(
                                    Deviation.CONFIG_MISMATCH,
                                    f"配置步骤「{setup_step.quote_name}」与标题不一致: " + "; ".join(mismatches),
                                    "HIGH"
                                ))
                        else:
                            # 有配置步骤但不在已知映射中
                            cd.issues.append(Deviation(
                                Deviation.CONFIG_MISMATCH,
                                f"配置步骤「{setup_step.quote_name}」(ID:{setup_step.quote_id})不在已知状态映射中，无法校验",
                                "MEDIUM"
                            ))
                    else:
                        cd.issues.append(Deviation(
                            Deviation.CONFIG_MISMATCH,
                            "标题包含配置状态信息但未找到前置配置步骤",
                            "HIGH"
                        ))

            # 检测5: 步骤为空
            if len(analysis.steps) == 0:
                cd.issues.append(Deviation(
                    Deviation.STEP_MISSING,
                    "用例没有任何步骤",
                    "HIGH"
                ))

            deviations.append(cd)

        print(f"[Phase 3] 偏差检测完成: {len([d for d in deviations if d.has_issues])} 条用例存在偏差")
        return deviations

    # ─────── Phase 4: 生成报告 ───────

    def generate_report(self, analyses, deviations, common_cases_raw=None):
        """
        汇总生成 AuditReport。

        Args:
            analyses: Phase 2 的结果
            deviations: Phase 3 的结果
            common_cases_raw: 公共用例列表

        Returns:
            AuditReport
        """
        report = AuditReport()
        report.business_cases = analyses
        report.common_cases = common_cases_raw or []
        report.deviations = deviations

        # 识别公共用例缺口：只收集确认在平台上不存在的引用
        unknown_quotes = {}  # quote_id -> list[case_name]
        for analysis in analyses:
            for step in analysis.steps:
                if step.quote_name.startswith("未知公共用例"):
                    # 再次确认平台上是否存在
                    verified = self._verify_case_exists(step.quote_id)
                    if not verified:
                        qid = step.quote_id
                        if qid not in unknown_quotes:
                            unknown_quotes[qid] = []
                        unknown_quotes[qid].append(analysis.case_name)

        for qid, refs in unknown_quotes.items():
            report.missing_commons.append({
                "quote_id": qid,
                "suggested_name": f"待确认公共用例(ID={qid})",
                "description": f"被 {len(refs)} 条业务用例引用但不在公共目录或知识库中",
                "referenced_by": refs
            })

        print(f"[Phase 4] 报告生成完成")
        return report

    # ─────── Phase 5: 修复执行 ───────

    def create_missing_commons(self, report, creations=None):
        """
        创建缺失的公共用例。

        Args:
            report: AuditReport
            creations: list[dict]，每个 dict 格式：
                {
                    "name": "【公共配置】xxx",
                    "parent": common_dir_id,
                    "description": "...",
                    "variables": [{"name": "...", "value": "..."}]
                }

        Returns:
            list[dict]: 创建结果
        """
        if self.dry_run:
            print("[Phase 5] dry_run 模式，跳过公共用例创建")
            return []

        if not creations:
            print("[Phase 5] 没有需要创建的公共用例")
            return []

        results = []
        for spec in creations:
            name = spec["name"]
            parent = spec.get("parent", self.common_dir_id)
            desc = spec.get("description", "")
            variables = spec.get("variables", [])

            res = self.client.create_case(
                name=name,
                directory_id=parent,
                description=desc,
                priority=2,
                variables=variables
            )

            if res.get("success"):
                new_id = res["data"]
                print(f"  ✅ 创建公共用例: {name} (ID: {new_id})")
                results.append({"name": name, "id": new_id, "success": True})
            else:
                print(f"  ❌ 创建失败: {name} - {res.get('message')}")
                results.append({"name": name, "id": None, "success": False, "error": res.get("message")})

        return results

    def fix_business_case_steps(self, case_id, fixes):
        """
        修复单条业务用例的步骤。

        Args:
            case_id: 业务用例ID
            fixes: list[dict]，每个 dict 格式之一：
                添加引用步骤: {"action": "add_quote", "order": 1, "quote_id": 66882, "name": "步骤名"}
                添加变量:     {"action": "add_var", "name": "变量名", "value": "变量值"}

        Returns:
            list[dict]: 每步修复的结果
        """
        if self.dry_run:
            print(f"[Phase 5] dry_run 模式，跳过修复 case {case_id}")
            return []

        results = []
        for fix in fixes:
            action = fix.get("action")

            if action == "add_quote":
                res = self.client.create_step(
                    case_id=case_id,
                    name=fix.get("name", "引用步骤"),
                    order=fix.get("order", 1),
                    type=1,
                    quote_id=fix.get("quote_id")
                )
                results.append({"action": action, "success": res.get("success"), "detail": res.get("message")})

            elif action == "add_var":
                res = self.client.create_variable(
                    case_id=case_id,
                    name=fix["name"],
                    value=fix["value"]
                )
                results.append({"action": action, "success": res.get("success", False), "detail": str(res)})

        return results

    def update_manifest(self, new_cases):
        """
        将新创建的公共用例追加到 manifest.json

        Args:
            new_cases: list[dict] - create_missing_commons 的返回结果
        """
        manifest = self.load_manifest()
        updated = False
        for nc in new_cases:
            if nc.get("success") and nc.get("id"):
                manifest[nc["name"]] = nc["id"]
                updated = True

        if updated:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            print(f"[Phase 5] manifest.json 已更新，新增 {sum(1 for nc in new_cases if nc.get('success'))} 条映射")

    # ─────── 一键流程 ───────

    def run_full_audit(self):
        """
        执行完整审计流程（Phase 1-4），返回报告。
        修复操作（Phase 5）需另行调用。

        Returns:
            AuditReport
        """
        print("=" * 60)
        print("用例调试器 - 全流程审计")
        print("=" * 60)

        # Phase 1
        print("\n[Phase 1] 采集数据...")
        business_raw = self.fetch_business_cases()
        common_raw = self.fetch_common_cases()

        # Phase 2
        print("\n[Phase 2] 解析状态机...")
        analyses = self.analyze_cases(business_raw, common_raw)

        # Phase 3
        print("\n[Phase 3] 偏差检测...")
        deviations = self.detect_deviations(analyses, common_raw)

        # Phase 4
        print("\n[Phase 4] 生成报告...")
        report = self.generate_report(analyses, deviations, common_raw)

        # 保存到文件
        output_dir = os.path.join(PROJECT_ROOT, "sandbox", "workspace")
        os.makedirs(output_dir, exist_ok=True)

        md_path = os.path.join(output_dir, f"debug_report_{report.timestamp}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report.to_markdown())

        json_path = os.path.join(output_dir, f"debug_report_{report.timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_json(), f, ensure_ascii=False, indent=2)

        print(f"\n📄 Markdown 报告: {md_path}")
        print(f"📦 JSON 报告: {json_path}")
        print("=" * 60)

        return report
