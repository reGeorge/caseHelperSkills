"""
Skills Discovery Tool - Skills发现和索引工具

自动扫描 skills/ 目录,索引所有可用的技能,并提供搜索和推荐功能。
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SkillInfo:
    """技能信息"""
    id: str
    name: str
    category: str
    path: str
    description: str
    keywords: List[str]
    api_class: Optional[str]
    main_file: Optional[str]
    documentation: Optional[str]
    capabilities: List[str]
    use_cases: List[str]
    required_params: List[str]
    optional_params: List[str]
    examples: List[str]


class SkillsDiscovery:
    """Skills发现和索引工具"""
    
    def __init__(self, skills_base_path: str = "."):
        """
        初始化发现工具
        
        Args:
            skills_base_path: skills基础路径
        """
        self.skills_base_path = Path(skills_base_path).absolute()
        self.skills: Dict[str, SkillInfo] = {}
        
        # 如果是当前目录,则设置为父目录
        if self.skills_base_path.name == "skills":
            self.skills_base_path = self.skills_base_path.parent
        
        self._load_registry()
    
    def _load_registry(self):
        """加载注册表"""
        # 查找skills目录
        skills_dir = None
        for path in [self.skills_base_path, self.skills_base_path / "skills"]:
            if path.is_dir() and (path / "lark-skills").exists():
                skills_dir = path
                break
        
        if not skills_dir:
            print(f"警告: 未找到skills目录,搜索路径: {self.skills_base_path}")
            skills_dir = self.skills_base_path  # 使用当前目录
        
        registry_file = skills_dir / "skills-registry.json"
        
        if registry_file.exists() and registry_file.stat().st_size > 10:  # 非空文件
            # 从注册表加载
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for skill_data in data.get('skills', []):
                        skill = SkillInfo(**skill_data)
                        self.skills[skill.id] = skill
            except Exception as e:
                print(f"加载注册表失败: {e},将重新扫描")
                self._discover_skills(skills_dir)
        else:
            # 自动扫描
            self._discover_skills(skills_dir)
    
    def _discover_skills(self, skills_dir: Path):
        """自动发现skills"""
        print(f"扫描目录: {skills_dir}")
        
        # 遍历所有分类目录
        for category_dir in sorted(skills_dir.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            print(f"  发现分类: {category_dir.name}")
            
            # 遍历分类下的每个skill
            for skill_dir in sorted(category_dir.iterdir()):
                if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                    continue
                
                # 查找SKILL.md文件
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue
                
                print(f"    解析skill: {skill_dir.name}")
                
                # 解析SKILL.md
                skill_info = self._parse_skill_md(skill_dir, category_dir.name)
                if skill_info:
                    self.skills[skill_info.id] = skill_info
                    print(f"      成功: {skill_info.name}")
        
        # 保存注册表
        self._save_registry(skills_dir)
    
    def _parse_skill_md(self, skill_dir: Path, category: str) -> Optional[SkillInfo]:
        """解析SKILL.md文件"""
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return None
        
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取信息
        skill_id = skill_dir.name
        name = self._extract_title(content) or skill_id
        description = self._extract_description(content)
        keywords = self._extract_keywords(content)
        capabilities = self._extract_capabilities(content)
        use_cases = self._extract_use_cases(content)
        examples = self._extract_examples(content)
        
        # 查找主文件
        main_files = list(skill_dir.glob("*.py"))
        main_file = main_files[0].name if main_files else None
        
        # 提取API类名
        api_class = self._extract_api_class(content, main_file) if main_file else None
        
        # 构建相对路径
        rel_path = str(skill_dir.relative_to(self.skills_base_path))
        
        return SkillInfo(
            id=skill_id,
            name=name,
            category=category,
            path=rel_path,
            description=description,
            keywords=keywords,
            api_class=api_class,
            main_file=main_file,
            documentation="SKILL.md",
            capabilities=capabilities,
            use_cases=use_cases,
            required_params=[],
            optional_params=[],
            examples=examples
        )
    
    def _extract_title(self, content: str) -> Optional[str]:
        """提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        # 查找功能说明或概述
        patterns = [
            r'功能说明\s*\n\s*-(.+)',
            r'概述\s*\n(.+?)(?:\n\n|\n#{1,3}\s)',
            r'^>\s*\*\*目标\*\*[:：]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # 默认返回第一段非标题内容
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('>'):
                return line[:100]
        
        return "暂无描述"
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 从文件名和标题提取
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            # 分割中英文
            words = re.findall(r'[\w]+|[\u4e00-\u9fff]+', title)
            keywords.extend(words)
        
        # 从描述中提取
        desc = self._extract_description(content)
        words = re.findall(r'[\w]+|[\u4e00-\u9fff]+', desc)
        keywords.extend(words[:5])  # 只取前5个
        
        # 去重并限制数量
        return list(set(keywords))[:10]
    
    def _extract_capabilities(self, content: str) -> List[str]:
        """提取能力列表"""
        capabilities = []
        
        # 查找"核心能力"或"功能说明"部分
        match = re.search(r'(核心能力|功能说明|Core Capabilities)\s*\n(?:-(.+)(?:\n|$))+', content, re.MULTILINE)
        if match:
            items = re.findall(r'-\s*(.+)', match.group(0))
            capabilities.extend([item.strip() for item in items])
        
        return capabilities[:5]
    
    def _extract_use_cases(self, content: str) -> List[str]:
        """提取使用场景"""
        use_cases = []
        
        # 查找"使用场景"部分
        match = re.search(r'(使用场景|Use Cases)\s*\n(?:-(.+)(?:\n|$))+', content, re.MULTILINE)
        if match:
            items = re.findall(r'-\s*(.+)', match.group(0))
            use_cases.extend([item.strip() for item in items])
        
        return use_cases[:3]
    
    def _extract_examples(self, content: str) -> List[str]:
        """提取示例"""
        examples = []
        
        # 查找"使用示例"或"示例"部分
        match = re.search(r'(使用示例|示例|Examples)\s*\n(?:-(.+)(?:\n|$))+', content, re.MULTILINE)
        if match:
            items = re.findall(r'-\s*(.+)', match.group(0))
            examples.extend([item.strip() for item in items])
        
        return examples[:2]
    
    def _extract_api_class(self, content: str, main_file: str) -> Optional[str]:
        """提取API类名"""
        # 简单的类名推断
        if main_file:
            # 从文件名推断类名
            class_name = ''.join(word.capitalize() for word in main_file.replace('.py', '').split('_'))
            return class_name
        return None
    
    def _save_registry(self, skills_dir: Path):
        """保存注册表"""
        registry_file = skills_dir / "skills-registry.json"
        
        data = {
            "skills": [asdict(skill) for skill in self.skills.values()]
        }
        
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def search(self, query: str, limit: int = 10) -> List[SkillInfo]:
        """
        搜索skills
        
        Args:
            query: 搜索关键词
            limit: 返回结果限制
        
        Returns:
            匹配的skill列表
        """
        query = query.lower()
        results = []
        
        for skill in self.skills.values():
            score = 0
            
            # ID匹配
            if query in skill.id.lower():
                score += 10
            
            # 名称匹配
            if query in skill.name.lower():
                score += 8
            
            # 描述匹配
            if query in skill.description.lower():
                score += 5
            
            # 关键词匹配
            for keyword in skill.keywords:
                if query in keyword.lower():
                    score += 3
            
            # 能力匹配
            for capability in skill.capabilities:
                if query in capability.lower():
                    score += 2
            
            # 使用场景匹配
            for use_case in skill.use_cases:
                if query in use_case.lower():
                    score += 2
            
            if score > 0:
                results.append((score, skill))
        
        # 按分数排序
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [skill for _, skill in results[:limit]]
    
    def get_by_id(self, skill_id: str) -> Optional[SkillInfo]:
        """根据ID获取skill"""
        return self.skills.get(skill_id)
    
    def get_by_category(self, category: str) -> List[SkillInfo]:
        """根据分类获取skills"""
        return [skill for skill in self.skills.values() if skill.category == category]
    
    def list_categories(self) -> List[str]:
        """列出所有分类"""
        categories = set(skill.category for skill in self.skills.values())
        return sorted(categories)
    
    def recommend(self, requirements: List[str]) -> List[SkillInfo]:
        """
        根据需求推荐skills
        
        Args:
            requirements: 需求列表
        
        Returns:
            推荐的skill列表
        """
        scores = {}
        
        for skill in self.skills.values():
            score = 0
            
            for req in requirements:
                req_lower = req.lower()
                
                # 检查所有文本字段
                if req_lower in skill.id.lower():
                    score += 10
                if req_lower in skill.name.lower():
                    score += 8
                if req_lower in skill.description.lower():
                    score += 5
                for keyword in skill.keywords:
                    if req_lower in keyword.lower():
                        score += 3
                for capability in skill.capabilities:
                    if req_lower in capability.lower():
                        score += 2
                for use_case in skill.use_cases:
                    if req_lower in use_case.lower():
                        score += 2
            
            if score > 0:
                scores[skill.id] = score
        
        # 排序
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: scores.get(s.id, 0),
            reverse=True
        )
        
        return sorted_skills


def main():
    """主函数 - 演示使用"""
    # 初始化发现工具
    discovery = SkillsDiscovery("skills")
    
    print(f"\n已发现 {len(discovery.skills)} 个skills\n")
    
    # 列出所有分类
    print("=== 所有分类 ===")
    for category in discovery.list_categories():
        print(f"- {category}")
    print()
    
    # 搜索示例
    print("=== 搜索'飞书' ===")
    results = discovery.search("飞书")
    for skill in results[:5]:
        print(f"- {skill.name}: {skill.description}")
    print()
    
    # 推荐示例
    print("=== 推荐用于'批量创建用例'的skills ===")
    recommendations = discovery.recommend(["批量", "创建", "用例"])
    for skill in recommendations[:3]:
        print(f"- {skill.name}")
        print(f"  路径: {skill.path}")
        print(f"  描述: {skill.description}")
        print(f"  使用场景: {', '.join(skill.use_cases)}")
        print()


if __name__ == "__main__":
    main()
