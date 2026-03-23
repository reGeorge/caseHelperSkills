"""
Skills Assistant - Skills智能推荐和使用助手

根据用户需求,智能推荐合适的skills,并提供使用指导。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class SkillRecommendation:
    """技能推荐结果"""
    skill_id: str
    skill_name: str
    path: str
    confidence: float  # 推荐置信度 0-1
    reason: str  # 推荐理由
    usage_hint: str  # 使用提示


class SkillsAssistant:
    """Skills智能推荐和使用助手"""
    
    def __init__(self, skills_base_path: str = "skills"):
        """
        初始化助手
        
        Args:
            skills_base_path: skills基础路径
        """
        from skills_discovery import SkillsDiscovery
        self.discovery = SkillsDiscovery(skills_base_path)
    
    def analyze_requirement(self, user_input: str) -> Tuple[List[str], List[str]]:
        """
        分析用户需求,提取关键词和意图
        
        Args:
            user_input: 用户输入
        
        Returns:
            (关键词列表, 意图列表)
        """
        import re
        
        # 关键词提取
        keywords = []
        
        # 提取中文词汇
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', user_input)
        keywords.extend(chinese_words)
        
        # 提取英文单词
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', user_input)
        keywords.extend([w.lower() for w in english_words])
        
        # 意图识别
        intents = []
        
        if any(word in user_input for word in ['读取', '获取', 'read', 'get', 'fetch']):
            intents.append('read')
        if any(word in user_input for word in ['写入', '保存', 'write', 'save']):
            intents.append('write')
        if any(word in user_input for word in ['批量', 'batch', '多个']):
            intents.append('batch')
        if any(word in user_input for word in ['创建', '新建', 'create', 'new']):
            intents.append('create')
        if any(word in user_input for word in ['分析', 'analyze', 'analysis']):
            intents.append('analyze')
        if any(word in user_input for word in ['调试', 'debug']):
            intents.append('debug')
        if any(word in user_input for word in ['飞书', 'feishu', 'lark']):
            intents.append('lark')
        if any(word in user_input for word in ['用例', 'case', 'test']):
            intents.append('case')
        if any(word in user_input for word in ['认证', '登录', 'auth', 'login']):
            intents.append('auth')
        
        return keywords, intents
    
    def recommend(self, user_input: str, top_k: int = 3) -> List[SkillRecommendation]:
        """
        根据用户需求推荐skills
        
        Args:
            user_input: 用户需求描述
            top_k: 返回推荐数量
        
        Returns:
            推荐结果列表
        """
        keywords, intents = self.analyze_requirement(user_input)
        
        # 使用发现工具搜索
        search_results = []
        for keyword in keywords:
            results = self.discovery.search(keyword)
            search_results.extend(results)
        
        # 使用推荐功能
        recommended = self.discovery.recommend(keywords + intents)
        
        # 合并结果并去重
        all_skills = {}
        for skill in search_results + recommended:
            if skill.id not in all_skills:
                all_skills[skill.id] = skill
        
        # 计算推荐分数
        recommendations = []
        for skill in all_skills.values():
            score = self._calculate_match_score(skill, keywords, intents)
            confidence = min(score / 100.0, 1.0)  # 转换为0-1
            
            if confidence > 0:
                reason = self._generate_reason(skill, keywords, intents)
                usage_hint = self._generate_usage_hint(skill)
                
                recommendations.append(SkillRecommendation(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    path=skill.path,
                    confidence=confidence,
                    reason=reason,
                    usage_hint=usage_hint
                ))
        
        # 按置信度排序
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        
        return recommendations[:top_k]
    
    def _calculate_match_score(self, skill, keywords: List[str], intents: List[str]) -> float:
        """计算匹配分数"""
        score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in skill.id.lower():
                score += 10
            if keyword_lower in skill.name.lower():
                score += 8
            if keyword_lower in skill.description.lower():
                score += 5
            
            for kw in skill.keywords:
                if keyword_lower in kw.lower():
                    score += 3
            
            for capability in skill.capabilities:
                if keyword_lower in capability.lower():
                    score += 2
            
            for use_case in skill.use_cases:
                if keyword_lower in use_case.lower():
                    score += 2
        
        # 意图加权
        for intent in intents:
            if intent in skill.description.lower():
                score += 5
            for kw in skill.keywords:
                if intent in kw.lower():
                    score += 3
        
        return score
    
    def _generate_reason(self, skill, keywords: List[str], intents: List[str]) -> str:
        """生成推荐理由"""
        reasons = []
        
        for keyword in keywords:
            if keyword.lower() in skill.name.lower():
                reasons.append(f"名称匹配'{keyword}'")
                break
        
        matched_keywords = []
        for keyword in keywords:
            for kw in skill.keywords:
                if keyword.lower() in kw.lower():
                    matched_keywords.append(keyword)
                    break
        
        if matched_keywords:
            reasons.append(f"关键词匹配: {', '.join(matched_keywords)}")
        
        matched_use_cases = []
        for keyword in keywords:
            for use_case in skill.use_cases:
                if keyword.lower() in use_case.lower():
                    matched_use_cases.append(use_case)
                    break
        
        if matched_use_cases:
            reasons.append(f"适用场景: {matched_use_cases[0]}")
        
        if not reasons:
            reasons.append(f"根据需求'{skill.description}'推荐")
        
        return "; ".join(reasons)
    
    def _generate_usage_hint(self, skill) -> str:
        """生成使用提示"""
        hints = []
        
        # 路径提示
        hints.append(f"位置: {skill.path}")
        
        # 使用场景
        if skill.use_cases:
            hints.append(f"场景: {skill.use_cases[0]}")
        
        # 主文件
        if skill.main_file:
            hints.append(f"主文件: {skill.main_file}")
        
        # API类
        if skill.api_class:
            hints.append(f"类名: {skill.api_class}")
        
        return " | ".join(hints)
    
    def get_usage_guide(self, skill_id: str) -> Optional[str]:
        """
        获取skill的使用指南
        
        Args:
            skill_id: skill ID
        
        Returns:
            使用指南文本
        """
        skill = self.discovery.get_by_id(skill_id)
        if not skill:
            return None
        
        # 读取SKILL.md文件
        skill_dir = self.discovery.skills_base_path / skill.path
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return None
        
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def format_recommendation(self, recommendation: SkillRecommendation) -> str:
        """
        格式化推荐结果为可读文本
        
        Args:
            recommendation: 推荐结果
        
        Returns:
            格式化的文本
        """
        lines = [
            f"## {recommendation.skill_name}",
            f"**置信度**: {recommendation.confidence:.1%}",
            f"**路径**: {recommendation.path}",
            f"",
            f"**推荐理由**: {recommendation.reason}",
            f"**使用提示**: {recommendation.usage_hint}",
            f"",
        ]
        
        return "\n".join(lines)
    
    def interactive_recommend(self, user_input: str) -> str:
        """
        交互式推荐,返回完整的使用建议
        
        Args:
            user_input: 用户需求
        
        Returns:
            完整建议文本
        """
        recommendations = self.recommend(user_input, top_k=3)
        
        if not recommendations:
            return f"未找到适合的skill,建议尝试其他关键词。\n\n可用的分类:\n" + \
                   "\n".join(f"- {cat}" for cat in self.discovery.list_categories())
        
        lines = [
            f"# 根据需求推荐Skills",
            f"",
            f"**您的需求**: {user_input}",
            f"",
            f"## 推荐结果 ({len(recommendations)}个)",
            f"",
        ]
        
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"### {i}. {rec.skill_name}")
            lines.append(f"**置信度**: {rec.confidence:.1%}")
            lines.append(f"**路径**: `skills/{rec.path}`")
            lines.append(f"")
            lines.append(f"**推荐理由**: {rec.reason}")
            lines.append(f"**使用提示**: {rec.usage_hint}")
            lines.append(f"")
        
        lines.append("---")
        lines.append("")
        lines.append("## 如何使用")
        lines.append("")
        
        # 获取最佳推荐的使用指南
        best_rec = recommendations[0]
        skill = self.discovery.get_by_id(best_rec.skill_id)
        if skill:
            lines.append(f"### 示例代码")
            lines.append("```python")
            lines.append(f"import sys")
            lines.append(f"sys.path.insert(0, 'skills/{skill.path}')")
            if skill.main_file:
                module_name = skill.main_file.replace('.py', '')
                lines.append(f"from {module_name} import {skill.api_class or 'main'}")
            lines.append("```")
            lines.append("")
            
            if skill.documentation:
                lines.append(f"**详细文档**: 查看 `skills/{skill.path}/{skill.documentation}`")
        
        return "\n".join(lines)


def main():
    """主函数 - 演示使用"""
    assistant = SkillsAssistant()
    
    # 示例1: 搜索飞书读取
    print("=== 示例1: 读取飞书表格 ===")
    result = assistant.interactive_recommend("我想读取飞书表格中的测试用例数据")
    print(result)
    print("\n" + "="*80 + "\n")
    
    # 示例2: 批量创建用例
    print("=== 示例2: 批量创建用例 ===")
    result = assistant.interactive_recommend("我需要批量创建测试用例到SDET平台")
    print(result)
    print("\n" + "="*80 + "\n")
    
    # 示例3: 用例分析
    print("=== 示例3: 用例分析 ===")
    result = assistant.interactive_recommend("分析测试用例的设计模式")
    print(result)


if __name__ == "__main__":
    main()
