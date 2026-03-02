"""
代码执行引擎
负责安全地执行Python代码并捕获输出
"""

import os
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any
from security import SecurityPolicy, SecurityError


class CodeExecutor:
    """代码执行器"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)

        self.skills_dir = Path(self.config['paths']['skills_dir'])
        self.sandbox_dir = Path(self.config['paths']['sandbox_dir'])
        self.workspace_dir = Path(self.config['paths']['workspace_dir'])

        self.security = SecurityPolicy()
        self.timeout = self.config['execution']['timeout']

        # 确保workspace目录存在
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

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
            raise SecurityError(error_msg)

    def _wrap_code(self, code: str) -> str:
        """包装代码，添加sys.path设置"""
        skills_dir_str = str(self.skills_dir).replace('\\', '\\\\')
        wrapper = f'''import sys
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
{code}
'''
        return wrapper

    async def execute(self, code: str, timeout: int = None) -> Dict[str, Any]:
        """
        执行Python代码

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

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'success': result.returncode == 0
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
