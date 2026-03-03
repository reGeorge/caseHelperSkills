"""
SDET平台登录工具
处理401鉴权失效场景，通过账号密码登录获取token
"""
import requests
import json
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
import urllib3

# 禁用SSL警告（测试平台使用自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SDETLogin:
    """SDET平台登录客户端"""
    
    def __init__(self, base_url: str = "https://sdet.ruishan.cc/api/sdet-base"):
        """
        初始化登录客户端
        
        Args:
            base_url: SDET平台基础URL
        """
        self.base_url = base_url
        self.login_url = f"{base_url}/user/login"
        
        # 请求头
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://sdet.ruishan.cc',
            'Referer': 'https://sdet.ruishan.cc/ap/login',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        登录SDET平台
        
        Args:
            username: 用户名（code字段）
            password: 密码（key字段）
            
        Returns:
            登录结果字典:
            {
                'success': bool,
                'token': str (如果成功),
                'user_info': dict (如果成功),
                'error': str (如果失败),
                'error_code': int (如果失败)
            }
        """
        # 构造请求体
        payload = {
            "code": username,
            "key": password
        }
        
        try:
            # 发送登录请求
            response = requests.post(
                self.login_url,
                headers=self.headers,
                json=payload,
                verify=False,  # 忽略SSL证书验证
                timeout=30
            )
            
            # 解析响应
            if response.status_code == 200:
                result = response.json()
                
                # 检查success字段（实际返回格式）
                if result.get('success') == True:
                    # 登录成功
                    data = result.get('data', {})
                    token = data.get('token', '')
                    
                    # 用户信息直接在data中
                    user_info = {
                        'id': data.get('id'),
                        'username': data.get('code', ''),
                        'name': data.get('name', ''),
                        'email': data.get('email', ''),
                        'role': data.get('role')
                    }
                    
                    return {
                        'success': True,
                        'token': token,
                        'user_info': user_info,
                        'message': result.get('resMessage', '登录成功')
                    }
                else:
                    # 业务错误
                    return {
                        'success': False,
                        'error': result.get('resMessage', '登录失败'),
                        'error_code': result.get('resCode', '-1')
                    }
            else:
                # HTTP错误
                return {
                    'success': False,
                    'error': f'HTTP错误: {response.status_code}',
                    'error_code': response.status_code
                }
        
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'error': f'网络连接失败: {str(e)}',
                'error_code': -1
            }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时，请稍后重试',
                'error_code': -1
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'登录异常: {str(e)}',
                'error_code': -1
            }
    
    def save_token_to_config(self, token: str, config_file: Optional[str] = None) -> bool:
        """
        将token保存到配置文件
        
        Args:
            token: SDET平台token
            config_file: 配置文件路径（默认为agent_service/config.yaml）
            
        Returns:
            是否保存成功
        """
        if not config_file:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent.parent
            config_file = project_root / "agent_service" / "config.yaml"
        
        try:
            # 读取现有配置
            config_file = Path(config_file)
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}
            
            # 确保secrets节点存在
            if 'secrets' not in config:
                config['secrets'] = {}
            
            # 更新token
            config['secrets']['SDET_API_TOKEN'] = token
            
            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            return True
        
        except Exception as e:
            print(f"保存token失败: {e}")
            return False
    
    def get_token_from_config(self, config_file: Optional[str] = None) -> Optional[str]:
        """
        从配置文件读取token
        
        Args:
            config_file: 配置文件路径（默认为agent_service/config.yaml）
            
        Returns:
            token字符串，如果不存在则返回None
        """
        if not config_file:
            project_root = Path(__file__).parent.parent.parent.parent
            config_file = project_root / "agent_service" / "config.yaml"
        
        try:
            config_file = Path(config_file)
            
            if not config_file.exists():
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            return config.get('secrets', {}).get('SDET_API_TOKEN')
        
        except Exception:
            return None


# 使用示例
if __name__ == "__main__":
    login = SDETLogin()
    
    # 方式1: 直接使用账号密码
    print("=" * 60)
    print("测试登录功能")
    print("=" * 60)
    
    username = input("请输入用户名: ")
    password = input("请输入密码: ")
    
    result = login.login(username, password)
    
    if result['success']:
        print("\n[OK] 登录成功！")
        print(f"Token: {result['token'][:20]}...")
        print(f"用户信息: {result['user_info']}")
        
        # 保存token
        if login.save_token_to_config(result['token']):
            print("\n[OK] Token已保存到配置文件")
        else:
            print("\n[FAIL] Token保存失败")
    else:
        print(f"\n[FAIL] 登录失败: {result['error']}")
        print(f"错误码: {result.get('error_code', 'N/A')}")
