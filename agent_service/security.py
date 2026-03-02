"""
安全策略模块
用于代码执行前的安全检查和权限控制
"""

import re
import ast
from typing import Set, List
from pathlib import Path


class SecurityPolicy:
    """安全策略管理器"""

    # 允许的模块白名单
    ALLOWED_MODULES: Set[str] = {
        'os', 'sys', 'json', 're', 'datetime', 'time',
        'requests', 'urllib', 'collections', 'itertools',
        'pathlib', 'typing', 'dataclasses', 'enum',
        # skills目录下的模块
        'lark_access_token', 'lark_sheet_reader', 'lark_sheet_writer',
        'platform_client', 'sdet_api_helper', 'case_ai_overview'
    }

    # 禁止的危险操作
    FORBIDDEN_OPERATIONS: List[str] = [
        'os.system', 'os.popen', 'subprocess.call',
        'eval(', 'exec(', 'compile(',
        '__import__',
    ]

    # 允许读取的路径
    ALLOWED_READ_PATHS: List[Path] = [
        Path("d:/Code/caseHelper/skills/"),
    ]

    # 禁止写入的路径（workspace以外的路径）
    FORBIDDEN_WRITE_PATTERNS: List[str] = [
        r'\.\.[\\/]',
        r'^[A-Za-z]:[\\/].*',
        r'^/',
    ]

    def __init__(self):
        self.workspace_dir = Path("d:/Code/caseHelper/sandbox/workspace")

    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        验证代码安全性

        Args:
            code: Python代码字符串

        Returns:
            (is_valid, error_message)
        """
        # 1. 检查危险操作
        for forbidden in self.FORBIDDEN_OPERATIONS:
            if forbidden in code:
                return False, f"禁止使用危险操作: {forbidden}"

        # 2. 检查导入语句
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.ALLOWED_MODULES:
                            return False, f"禁止导入模块: {alias.name}"

                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in self.ALLOWED_MODULES:
                        return False, f"禁止导入模块: {node.module}"
        except SyntaxError as e:
            # 这里不阻止语法错误，让执行阶段自然失败
            pass

        # 3. 检查文件路径操作（简单模式匹配）
        self._check_file_operations(code)

        return True, ""

    def _check_file_operations(self, code: str) -> None:
        """检查文件路径操作是否安全"""
        # 检查 open() 调用中的路径
        open_pattern = r'open\s*\(\s*["\']([^"\']+)["\']'
        matches = re.findall(open_pattern, code)

        for path in matches:
            # 检查是否尝试访问workspace以外的路径
            path_obj = Path(path)
            # 相对路径中包含 .. 或不以 ./ 开头（且不是文件名）
            if '..' in str(path_obj) or (str(path_obj).startswith('/') or (len(str(path_obj)) > 2 and str(path_obj)[1] == ':' and str(path_obj)[2] == '\\')):
                raise SecurityError(f"禁止访问路径: {path}. 所有文件操作必须在当前工作目录 ./ 中")

    def validate_workspace_file(self, filepath: str) -> bool:
        """验证文件路径是否在workspace目录中"""
        path = Path(filepath)
        # 如果是相对路径，认为是在workspace中
        return not path.is_absolute()


class SecurityError(Exception):
    """安全策略异常"""
    pass
