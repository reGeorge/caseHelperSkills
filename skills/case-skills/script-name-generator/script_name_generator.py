"""
自动化用例标题生成器
自动生成测试用例的脚本名称和脚本步骤
"""
import json
import re
import requests
from typing import Optional

class ScriptNameGenerator:
    """自动化用例标题生成器"""
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            app_id: 飞书应用ID(可选,处理飞书表格时需要)
            app_secret: 飞书应用密钥(可选,处理飞书表格时需要)
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """获取飞书access_token"""
        if not self.app_id or not self.app_secret:
            raise ValueError("缺少飞书凭证,请设置app_id和app_secret")
        
        if self.access_token:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('code') == 0:
            self.access_token = result['tenant_access_token']
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")
    
    def extract_last_expect_result(self, expect_result: str) -> str:
        """
        提取期望结果的最后一句话
        
        Args:
            expect_result: 期望结果文本
            
        Returns:
            最后一句话
        """
        if not expect_result:
            return ""
        
        # 移除步骤编号(如 "1." "2." 等)
        lines = re.split(r'\n+', expect_result)
        
        # 找到最后一个步骤
        for line in reversed(lines):
            # 提取步骤内容(去掉编号)
            match = re.search(r'\d+\.\s*(.+)', line)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到编号,返回最后一行
        return lines[-1].strip() if lines else ""
    
    def generate_script_name(self, case_name: str, expect_result: str) -> str:
        """
        生成脚本名称
        
        Args:
            case_name: 用例名称
            expect_result: 期望结果
            
        Returns:
            脚本名称
        """
        last_result = self.extract_last_expect_result(expect_result)
        
        if not case_name:
            return last_result
        
        if not last_result:
            return case_name
        
        # 拼接用例名称和最后一句话
        return f"{case_name} - {last_result}"
    
    def split_into_steps(self, text: str) -> str:
        """
        将文本拆分成步骤
        
        Args:
            text: 文本内容
            
        Returns:
            格式化的步骤文本
        """
        if not text:
            return ""
        
        # 按逗号、句号、顿号等分隔符拆分
        # 优先按句号拆分,如果没有句号则按逗号拆分
        separators = ['。', '，', '、', '；', ',', ';']
        
        # 尝试按优先级拆分
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                steps = []
                step_num = 1
                
                for part in parts:
                    part = part.strip()
                    if part:
                        # 移除可能存在的括号标注(如 "（正向）")
                        part = re.sub(r'[（(][^）)]*[）)]', '', part)
                        part = part.strip()
                        
                        if part:
                            steps.append(f"{step_num}. {part}")
                            step_num += 1
                
                if steps:
                    return "\n".join(steps)
        
        # 如果没有分隔符,返回原文本作为第一步
        return f"1. {text}"
    
    def _read_sheet_data(self, spreadsheet_token: str, sheet_id: str) -> list:
        """读取飞书表格数据"""
        access_token = self._get_access_token()
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"读取表格失败: {result}")
        
        values = result['data']['valueRange']['values']
        if len(values) < 2:
            return []
        
        # 第一行是表头
        headers = values[0]
        cases = []
        
        # 从第二行开始读取数据
        for row in values[1:]:
            case = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    case[header] = row[i]
                else:
                    case[header] = None
            cases.append(case)
        
        return cases
    
    def _write_to_sheet(self, spreadsheet_token: str, sheet_id: str, 
                        data: list, start_row: int = 2) -> bool:
        """写入飞书表格"""
        access_token = self._get_access_token()
        
        # 先更新表头
        self._update_headers(spreadsheet_token, sheet_id, access_token)
        
        # 准备写入数据
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        values = []
        for case in data:
            row = [
                case.get('脚本名称', ''),
                case.get('脚本步骤', '')
            ]
            values.append(row)
        
        # Z列:脚本名称, AA列:脚本步骤
        range_str = f"{sheet_id}!Z{start_row}:AA{start_row + len(values) - 1}"
        
        payload = {
            "valueRange": {
                "range": range_str,
                "values": values
            }
        }
        
        response = requests.put(url, headers=headers, json=payload)
        result = response.json()
        
        return result.get('code') == 0
    
    def _update_headers(self, spreadsheet_token: str, sheet_id: str, access_token: str) -> bool:
        """更新表头"""
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "valueRange": {
                "range": f"{sheet_id}!Z1:AA1",
                "values": [["脚本名称", "脚本步骤"]]
            }
        }
        
        response = requests.put(url, headers=headers, json=payload)
        result = response.json()
        
        return result.get('code') == 0
    
    def generate_from_sheet(self, spreadsheet_token: str, sheet_id: str) -> dict:
        """
        从飞书表格读取数据,生成脚本名称和步骤,并写回表格
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID
            
        Returns:
            处理结果
        """
        try:
            # 读取数据
            cases = self._read_sheet_data(spreadsheet_token, sheet_id)
            
            # 生成脚本名称和步骤
            for case in cases:
                case_name = case.get('用例名称', '')
                expect_result = case.get('期望结果', '')
                
                case['脚本名称'] = self.generate_script_name(case_name, expect_result)
                case['脚本步骤'] = self.split_into_steps(case['脚本名称'])
            
            # 写回表格
            success = self._write_to_sheet(spreadsheet_token, sheet_id, cases)
            
            return {
                'success': success,
                'total_count': len(cases),
                'success_count': len(cases) if success else 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_from_local(self, json_file: str, output_file: Optional[str] = None) -> dict:
        """
        从本地JSON文件读取数据,生成脚本名称和步骤
        
        Args:
            json_file: 输入JSON文件路径
            output_file: 输出JSON文件路径(可选,默认在原文件名后添加_with_script_info)
            
        Returns:
            处理结果
        """
        try:
            # 读取数据
            with open(json_file, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            
            # 生成脚本名称和步骤
            for case in cases:
                case_name = case.get('用例名称', '')
                expect_result = case.get('期望结果', '')
                
                case['脚本名称'] = self.generate_script_name(case_name, expect_result)
                case['脚本步骤'] = self.split_into_steps(case['脚本名称'])
            
            # 保存到文件
            if not output_file:
                base_name = json_file.rsplit('.', 1)[0]
                output_file = f"{base_name}_with_script_info.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'total_count': len(cases),
                'output_file': output_file,
                'cases': cases
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 使用示例
if __name__ == "__main__":
    import os
    
    # 示例1: 从本地JSON文件生成
    generator = ScriptNameGenerator()
    result = generator.generate_from_local("test_cases.json")
    
    if result['success']:
        print(f"处理成功: {result['total_count']} 条")
        print(f"输出文件: {result['output_file']}")
    else:
        print(f"处理失败: {result['error']}")
    
    # 示例2: 从飞书表格生成(需要凭证)
    # generator = ScriptNameGenerator(
    #     app_id=os.getenv('LARK_APP_ID'),
    #     app_secret=os.getenv('LARK_APP_SECRET')
    # )
    # result = generator.generate_from_sheet("token", "sheet_id")
