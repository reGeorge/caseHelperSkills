"""
代码执行引擎
负责安全地执行Python代码并捕获输出
支持代码缓存和智能重试机制
"""

import os
import subprocess
import tempfile
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional
from security import SecurityPolicy, SecurityError


class CodeExecutor:
    """代码执行器（优化版）"""

    # 输出长度限制（字符数）
    MAX_OUTPUT_LENGTH = 5000
    # 最大重试次数
    MAX_RETRIES = 3

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)

        self.skills_dir = Path(self.config['paths']['skills_dir'])
        self.sandbox_dir = Path(self.config['paths']['sandbox_dir'])
        self.workspace_dir = Path(self.config['paths']['workspace_dir'])

        self.security = SecurityPolicy()
        self.timeout = self.config['execution']['timeout']

        # 确保workspace目录存在
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # 缓存wrapper代码（避免重复生成）
        self._wrapper_template = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _build_env(self) -> Dict[str, str]:
        """动态注入环境变量"""
        env_vars = os.environ.copy()

        # 注入凭证到环境变量
        secrets = self.config.get('secrets', {})
        for key, value in secrets.items():
            env_vars[key] = str(value)

        return env_vars

    def _validate_code(self, code: str) -> None:
        """验证代码安全性"""
        is_valid, error_msg = self.security.validate_code(code)
        if not is_valid:
            # 简化错误信息，不包含堆栈
            raise SecurityError(f"安全检查失败: {error_msg}")

    def _get_wrapper_template(self) -> str:
        """获取wrapper代码模板（缓存）"""
        if self._wrapper_template is None:
            skills_dir_str = str(self.skills_dir).replace('\\', '\\\\')
            self._wrapper_template = f'''import sys
import os
from pathlib import Path

# 添加skills目录到Python路径
skills_dir = Path(r"{skills_dir_str}")
sys.path.insert(0, str(skills_dir))

# 添加各个skill子目录
sys.path.insert(0, str(skills_dir / "lark-skills" / "lark-access-token"))
sys.path.insert(0, str(skills_dir / "lark-skills" / "lark-sheet-reader"))
sys.path.insert(0, str(skills_dir / "lark-skills" / "lark-sheet-writer"))
sys.path.insert(0, str(skills_dir / "lark-skills" / "lark-api-helper"))
sys.path.insert(0, str(skills_dir / "sdet-skills" / "platform-client"))
sys.path.insert(0, str(skills_dir / "sdet-skills" / "sdet-api-helper"))
sys.path.insert(0, str(skills_dir / "case-skills" / "case-ai-overview"))

# 用户代码
{{code}}
'''
        return self._wrapper_template

    def _wrap_code(self, code: str) -> str:
        """包装代码，添加sys.path设置（使用缓存模板）"""
        template = self._get_wrapper_template()
        # 使用format替换占位符
        return template.replace('{{code}}', code).replace('{code}', code)

    def _truncate_output(self, output: str) -> str:
        """截断过长的输出"""
        if len(output) <= self.MAX_OUTPUT_LENGTH:
            return output

        truncated = output[:self.MAX_OUTPUT_LENGTH]
        # 在最后一个换行符处截断
        last_newline = truncated.rfind('\n')
        if last_newline > self.MAX_OUTPUT_LENGTH - 100:
            truncated = truncated[:last_newline]

        return truncated + f"\n...[输出已截断，超过{self.MAX_OUTPUT_LENGTH}字符限制]"

    def _fix_common_errors(self, code: str, stderr: str) -> Optional[str]:
        """智能修复常见错误"""
        # 1. ImportError: 检查是否是skills模块导入问题
        if 'ImportError' in stderr and 'No module named' in stderr:
            # 自动添加缺失的路径（如果明确是skills模块）
            match = re.search(r"No module named '(\w+)'", stderr)
            if match:
                module_name = match.group(1)
                # 如果模块名称包含lark、sdet、case等，自动添加路径
                if any(keyword in module_name.lower() for keyword in ['lark', 'sdet', 'case']):
                    return code  # 保持原样，因为wrapper已经包含了路径

        # 2. SyntaxError: 无法自动修复
        if 'SyntaxError' in stderr:
            return None

        # 3. FileNotFoundError 或 OSError: 检查路径问题
        if 'FileNotFoundError' in stderr or 'OSError' in stderr:
            # 如果包含 ../skills 但被拒绝，提示使用绝对路径
            if '../skills' in code:
                # 移除../skills，使用Path对象
                new_code = code.replace('../skills', 'Path(r"d:/Code/caseHelper/skills")')
                return new_code

        return None  # 无法自动修复

    async def execute_once(self, code: str, timeout: int = None) -> Dict[str, Any]:
        """
        执行一次Python代码

        Args:
            code: Python代码字符串
            timeout: 超时时间（秒），默认使用配置文件中的值

        Returns:
            包含执行结果的字典
        """
        # 1. 安全检查
        self._validate_code(code)

        # 2. 准备workspace目录
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # 3. 写入临时文件
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as f:
            f.write(self._wrap_code(code))
            temp_file = f.name

        try:
            # 4. 执行代码（严格限制在工作目录）
            actual_timeout = timeout if timeout is not None else self.timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=actual_timeout,
                cwd=str(self.workspace_dir),
                env=self._build_env()
            )

            # 5. 截断过长的输出
            stdout = self._truncate_output(result.stdout)
            stderr = self._truncate_output(result.stderr)

            return {
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': result.returncode,
                'success': result.returncode == 0,
                'truncated': len(result.stdout) > self.MAX_OUTPUT_LENGTH
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'执行超时（超过{actual_timeout}秒）',
                'exit_code': -1,
                'success': False
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'success': False
            }
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass

    async def execute(self, code: str, timeout: int = None) -> Dict[str, Any]:
        """
        执行Python代码（支持智能重试）

        Args:
            code: Python代码字符串
            timeout: 超时时间（秒），默认使用配置文件中的值

        Returns:
            包含执行结果的字典
        """
        # 首次执行
        result = await self.execute_once(code, timeout)

        # 如果成功，直接返回
        if result['success']:
            return result

        # 如果失败，尝试智能重试
        for retry in range(self.MAX_RETRIES):
            if not result['success'] and result['stderr']:
                # 尝试自动修复
                fixed_code = self._fix_common_errors(code, result['stderr'])

                if fixed_code and fixed_code != code:
                    print(f"尝试自动修复并重试 ({retry + 1}/{self.MAX_RETRIES})...")
                    code = fixed_code
                    result = await self.execute_once(code, timeout)

                    if result['success']:
                        result['auto_fixed'] = True
                        result['retry_count'] = retry + 1
                        return result

        # 最终失败，返回最后的结果
        return result

