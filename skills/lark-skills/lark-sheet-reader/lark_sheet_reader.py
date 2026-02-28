import requests
import json
import argparse
import sys
from typing import List, Dict, Optional, Any

class LarkSheetReader:
    """
    飞书表格内容读取器
    Lark Sheet Content Reader
    
    用于读取飞书表格内容并转换为JSON格式
    Used to read Lark spreadsheet content and convert to JSON format
    """
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化读取器
        Initialize the reader
        
        Args:
            app_id: 飞书应用ID | Lark application ID
            app_secret: 飞书应用密钥 | Lark application secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"
        
    def get_access_token(self) -> str:
        """
        获取访问令牌
        Get access token
        
        Returns:
            access_token: 访问令牌 | Access token
            
        Raises:
            Exception: 获取token失败时抛出异常 | Exception when failed to get token
        """
        url = f"{self.base_url}/auth/v3/app_access_token/internal/"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("app_access_token")
                return self.access_token
            else:
                raise Exception(f"获取access_token失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def read_sheet(self, spreadsheet_token: str, sheet_id: str = None) -> List[Dict[str, Any]]:
        """
        读取指定工作表内容
        Read specified sheet content
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID，不指定则读取第一个工作表 | Sheet ID, read first sheet if not specified
            
        Returns:
            List[Dict]: 工作表数据列表 | Sheet data list
        """
        if not self.access_token:
            self.get_access_token()
        
        if not sheet_id:
            sheet_id = self._get_first_sheet_id(spreadsheet_token)
        
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                values = result.get("data", {}).get("valueRange", {}).get("values", [])
                return self._convert_to_json(values)
            else:
                raise Exception(f"读取工作表失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def read_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        从URL读取表格内容
        Read sheet content from URL
        
        Args:
            url: 飞书表格URL | Lark spreadsheet URL
            
        Returns:
            List[Dict]: 工作表数据列表 | Sheet data list
        """
        spreadsheet_token, sheet_id = self._parse_url(url)
        return self.read_sheet(spreadsheet_token, sheet_id)
    
    def _get_first_sheet_id(self, spreadsheet_token: str) -> str:
        """
        获取第一个工作表ID
        Get first sheet ID
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            
        Returns:
            str: 第一个工作表ID | First sheet ID
        """
        url = f"{self.base_url}/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                sheets = result.get("data", {}).get("sheets", [])
                if sheets:
                    return sheets[0].get("sheet_id")
                else:
                    raise Exception("表格中没有工作表")
            else:
                raise Exception(f"获取工作表列表失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def _parse_url(self, url: str) -> tuple:
        """
        解析飞书表格URL
        Parse Lark spreadsheet URL
        
        Args:
            url: 飞书表格URL | Lark spreadsheet URL
            
        Returns:
            tuple: (spreadsheet_token, sheet_id)
        """
        import re
        
        # 提取spreadsheet_token
        match = re.search(r'/sheets/([a-zA-Z0-9]+)', url)
        if not match:
            raise Exception("无法从URL中提取spreadsheet_token")
        spreadsheet_token = match.group(1)
        
        # 提取sheet_id
        match = re.search(r'sheet=([a-zA-Z0-9]+)', url)
        sheet_id = match.group(1) if match else None
        
        return spreadsheet_token, sheet_id
    
    def _convert_to_json(self, values: List[List[str]]) -> List[Dict[str, Any]]:
        """
        将表格数据转换为JSON格式
        Convert sheet data to JSON format
        
        Args:
            values: 表格数据（二维数组） | Sheet data (2D array)
            
        Returns:
            List[Dict]: JSON格式的数据列表 | Data list in JSON format
        """
        if not values or len(values) < 2:
            return []
        
        # 第一行作为表头
        headers = values[0]
        
        # 转换数据
        result = []
        for row in values[1:]:
            # 跳过空行
            if not any(row):
                continue
            
            # 创建字典，使用表头作为key
            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    key = headers[i]
                    # 处理空值
                    row_dict[key] = cell if cell else None
            
            result.append(row_dict)
        
        return result
    
    def to_json(self, data: List[Dict[str, Any]], indent: int = 2) -> str:
        """
        将数据转换为JSON字符串
        Convert data to JSON string
        
        Args:
            data: 数据列表 | Data list
            indent: 缩进空格数 | Indentation spaces
            
        Returns:
            str: JSON字符串 | JSON string
        """
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    def save_to_file(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        将数据保存到JSON文件
        Save data to JSON file
        
        Args:
            data: 数据列表 | Data list
            filename: 文件名 | Filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")


def main():
    """
    主函数 - 命令行入口
    Main function - Command line entry
    """
    parser = argparse.ArgumentParser(description='飞书表格内容读取器 | Lark Sheet Reader')
    parser.add_argument('--app-id', required=True, help='飞书应用ID | Lark app ID')
    parser.add_argument('--app-secret', required=True, help='飞书应用密钥 | Lark app secret')
    parser.add_argument('--url', help='飞书表格URL | Lark spreadsheet URL')
    parser.add_argument('--spreadsheet-token', help='表格token | Spreadsheet token')
    parser.add_argument('--sheet-id', help='工作表ID | Sheet ID')
    parser.add_argument('--output', help='输出文件名 | Output filename')
    
    args = parser.parse_args()
    
    try:
        reader = LarkSheetReader(args.app_id, args.app_secret)
        
        if args.url:
            data = reader.read_from_url(args.url)
        elif args.spreadsheet_token:
            data = reader.read_sheet(args.spreadsheet_token, args.sheet_id)
        else:
            print("错误：请提供 --url 或 --spreadsheet-token 参数")
            sys.exit(1)
        
        # 输出JSON
        json_output = reader.to_json(data)
        print(json_output)
        
        # 保存到文件
        if args.output:
            reader.save_to_file(data, args.output)
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
