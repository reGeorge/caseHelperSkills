import requests
import json
import argparse
import sys
from typing import List, Dict, Optional, Any, Tuple

class LarkSheetWriter:
    """
    飞书表格记录写入器
    Lark Sheet Record Writer
    
    用于写入和编辑飞书表格的记录
    Used to write and edit records in Lark spreadsheets
    """
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化写入器
        Initialize the writer
        
        Args:
            app_id: 飞书应用ID | Lark application ID
            app_secret: 飞书应用密钥 | Lark application secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"
        self.headers = None
    
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
                self.headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                return self.access_token
            else:
                raise Exception(f"获取access_token失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        Get request headers
        
        Returns:
            Dict[str, str]: 请求头 | Request headers
        """
        if not self.headers:
            self.get_access_token()
        return self.headers
    
    def get_sheet_headers(self, spreadsheet_token: str, sheet_id: str) -> List[str]:
        """
        获取工作表表头
        Get sheet headers
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            
        Returns:
            List[str]: 表头列表 | Headers list
        """
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                values = result.get("data", {}).get("valueRange", {}).get("values", [])
                if values:
                    return values[0]  # 第一行作为表头
                else:
                    return []
            else:
                raise Exception(f"获取工作表数据失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def get_sheet_data(self, spreadsheet_token: str, sheet_id: str) -> List[List[str]]:
        """
        获取工作表数据
        Get sheet data
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            
        Returns:
            List[List[str]]: 工作表数据 | Sheet data
        """
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("valueRange", {}).get("values", [])
            else:
                raise Exception(f"获取工作表数据失败: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {e}")
    
    def write_record(self, spreadsheet_token: str, sheet_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        写入新记录
        Write new record
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            record: 记录数据 | Record data
            
        Returns:
            Dict[str, Any]: 操作结果 | Operation result
        """
        try:
            # 获取表头
            headers = self.get_sheet_headers(spreadsheet_token, sheet_id)
            if not headers:
                return {
                    "success": False,
                    "message": "工作表无表头数据",
                    "error": "Sheet has no header data"
                }
            
            # 构建行数据
            row_data = []
            for header in headers:
                row_data.append(record.get(header, ""))
            
            # 获取当前数据以确定插入位置
            data = self.get_sheet_data(spreadsheet_token, sheet_id)
            insert_row = len(data) + 1  # 插入到末尾
            
            # 构建范围
            start_col = self._col_number_to_letter(1)
            end_col = self._col_number_to_letter(len(headers))
            range_str = f"{sheet_id}!{start_col}{insert_row}:{end_col}{insert_row}"
            
            # 写入数据
            return self._write_range(spreadsheet_token, range_str, [row_data])
            
        except Exception as e:
            return {
                "success": False,
                "message": "写入记录失败",
                "error": str(e)
            }
    
    def write_records(self, spreadsheet_token: str, sheet_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量写入多条记录
        Batch write multiple records
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            records: 记录列表 | Records list
            
        Returns:
            Dict[str, Any]: 操作结果 | Operation result
        """
        try:
            # 获取表头
            headers = self.get_sheet_headers(spreadsheet_token, sheet_id)
            if not headers:
                return {
                    "success": False,
                    "message": "工作表无表头数据",
                    "error": "Sheet has no header data"
                }
            
            # 构建行数据
            rows_data = []
            for record in records:
                row_data = []
                for header in headers:
                    row_data.append(record.get(header, ""))
                rows_data.append(row_data)
            
            # 获取当前数据以确定插入位置
            data = self.get_sheet_data(spreadsheet_token, sheet_id)
            insert_row = len(data) + 1  # 插入到末尾
            
            # 构建范围
            start_col = self._col_number_to_letter(1)
            end_col = self._col_number_to_letter(len(headers))
            end_row = insert_row + len(rows_data) - 1
            range_str = f"{sheet_id}!{start_col}{insert_row}:{end_col}{end_row}"
            
            # 写入数据
            result = self._write_range(spreadsheet_token, range_str, rows_data)
            result["data"] = {
                "inserted_rows": len(rows_data),
                "updated_rows": 0
            }
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": "批量写入记录失败",
                "error": str(e)
            }
    
    def update_record(self, spreadsheet_token: str, sheet_id: str, condition: Dict[str, Any], 
                     update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于条件更新记录
        Update record based on condition
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            condition: 更新条件 | Update condition
            update_data: 更新数据 | Update data
            
        Returns:
            Dict[str, Any]: 操作结果 | Operation result
        """
        try:
            # 获取表头和数据
            headers = self.get_sheet_headers(spreadsheet_token, sheet_id)
            if not headers:
                return {
                    "success": False,
                    "message": "工作表无表头数据",
                    "error": "Sheet has no header data"
                }
            
            data = self.get_sheet_data(spreadsheet_token, sheet_id)
            if not data or len(data) < 2:  # 至少需要表头和一行数据
                return {
                    "success": False,
                    "message": "工作表无数据",
                    "error": "Sheet has no data"
                }
            
            # 查找符合条件的行
            updated_rows = 0
            for i, row in enumerate(data[1:], start=2):  # 从第二行开始（第一行是表头）
                # 检查是否符合条件
                match = True
                for key, value in condition.items():
                    if key not in headers:
                        match = False
                        break
                    col_index = headers.index(key)
                    if col_index >= len(row) or row[col_index] != str(value):
                        match = False
                        break
                
                if match:
                    # 构建更新后的数据
                    updated_row = list(row)
                    for key, value in update_data.items():
                        if key in headers:
                            col_index = headers.index(key)
                            if col_index >= len(updated_row):
                                # 扩展行数据
                                updated_row.extend([""] * (col_index - len(updated_row) + 1))
                            updated_row[col_index] = str(value)
                    
                    # 写入更新后的数据
                    start_col = self._col_number_to_letter(1)
                    end_col = self._col_number_to_letter(len(headers))
                    range_str = f"{sheet_id}!{start_col}{i}:{end_col}{i}"
                    
                    result = self._write_range(spreadsheet_token, range_str, [updated_row])
                    if result["success"]:
                        updated_rows += 1
            
            return {
                "success": True,
                "message": f"成功更新 {updated_rows} 行",
                "data": {
                    "updated_rows": updated_rows,
                    "inserted_rows": 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": "更新记录失败",
                "error": str(e)
            }
    
    def import_from_json(self, spreadsheet_token: str, sheet_id: str, json_file: str, 
                        clear_existing: bool = False) -> Dict[str, Any]:
        """
        从JSON文件导入数据
        Import data from JSON file
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            sheet_id: 工作表ID | Sheet ID
            json_file: JSON文件路径 | JSON file path
            clear_existing: 是否清空现有数据 | Whether to clear existing data
            
        Returns:
            Dict[str, Any]: 操作结果 | Operation result
        """
        try:
            # 读取JSON文件
            with open(json_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            if not isinstance(records, list):
                return {
                    "success": False,
                    "message": "JSON文件格式错误，应为数组",
                    "error": "JSON file format error, should be an array"
                }
            
            if clear_existing:
                # 清空现有数据（保留表头）
                headers = self.get_sheet_headers(spreadsheet_token, sheet_id)
                if headers:
                    # 只保留表头
                    range_str = f"{sheet_id}!A2:Z1000"  # 清空从第二行开始的数据
                    self._write_range(spreadsheet_token, range_str, [[]])
            
            # 批量写入数据
            return self.write_records(spreadsheet_token, sheet_id, records)
            
        except Exception as e:
            return {
                "success": False,
                "message": "导入数据失败",
                "error": str(e)
            }
    
    def _write_range(self, spreadsheet_token: str, range_str: str, values: List[List[str]]) -> Dict[str, Any]:
        """
        写入指定范围的数据
        Write data to specified range
        
        Args:
            spreadsheet_token: 表格token | Spreadsheet token
            range_str: 范围字符串 | Range string
            values: 数据值 | Data values
            
        Returns:
            Dict[str, Any]: 操作结果 | Operation result
        """
        url = f"{self.base_url}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
        
        data = {
            "valueRange": {
                "values": values
            }
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return {
                    "success": True,
                    "message": "写入成功",
                    "data": {
                        "updated_rows": len(values),
                        "inserted_rows": len(values)
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"写入失败: {result.get('msg')}",
                    "error": result.get('msg')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": "请求异常",
                "error": str(e)
            }
    
    def _col_number_to_letter(self, col: int) -> str:
        """
        将列号转换为字母
        Convert column number to letter
        
        Args:
            col: 列号 | Column number
            
        Returns:
            str: 列字母 | Column letter
        """
        letter = ""
        while col > 0:
            col, remainder = divmod(col - 1, 26)
            letter = chr(65 + remainder) + letter
        return letter
    
    def validate_data(self, records: List[Dict[str, Any]], required_fields: List[str]) -> Dict[str, Any]:
        """
        验证数据格式
        Validate data format
        
        Args:
            records: 记录列表 | Records list
            required_fields: 必填字段 | Required fields
            
        Returns:
            Dict[str, Any]: 验证结果 | Validation result
        """
        errors = []
        
        for i, record in enumerate(records, start=1):
            for field in required_fields:
                if field not in record or not record[field]:
                    errors.append(f"记录 {i} 缺少必填字段: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


def main():
    """
    主函数 - 命令行入口
    Main function - Command line entry
    """
    parser = argparse.ArgumentParser(description='飞书表格记录写入器 | Lark Sheet Writer')
    parser.add_argument('--app-id', required=True, help='飞书应用ID | Lark app ID')
    parser.add_argument('--app-secret', required=True, help='飞书应用密钥 | Lark app secret')
    parser.add_argument('--spreadsheet-token', required=True, help='表格token | Spreadsheet token')
    parser.add_argument('--sheet-id', required=True, help='工作表ID | Sheet ID')
    parser.add_argument('--action', required=True, choices=['write', 'update', 'import'], 
                        help='操作类型 | Action type')
    parser.add_argument('--record', help='单条记录数据（JSON格式） | Single record data (JSON format)')
    parser.add_argument('--records', help='多条记录数据（JSON格式） | Multiple records data (JSON format)')
    parser.add_argument('--condition', help='更新条件（JSON格式） | Update condition (JSON format)')
    parser.add_argument('--update-data', help='更新数据（JSON格式） | Update data (JSON format)')
    parser.add_argument('--json-file', help='JSON文件路径 | JSON file path')
    parser.add_argument('--clear-existing', action='store_true', help='是否清空现有数据 | Whether to clear existing data')
    
    args = parser.parse_args()
    
    try:
        writer = LarkSheetWriter(args.app_id, args.app_secret)
        
        if args.action == 'write':
            if args.record:
                record = json.loads(args.record)
                result = writer.write_record(args.spreadsheet_token, args.sheet_id, record)
            elif args.records:
                records = json.loads(args.records)
                result = writer.write_records(args.spreadsheet_token, args.sheet_id, records)
            else:
                print("错误：写入操作需要 --record 或 --records 参数")
                sys.exit(1)
        
        elif args.action == 'update':
            if not args.condition or not args.update_data:
                print("错误：更新操作需要 --condition 和 --update-data 参数")
                sys.exit(1)
            condition = json.loads(args.condition)
            update_data = json.loads(args.update_data)
            result = writer.update_record(args.spreadsheet_token, args.sheet_id, condition, update_data)
        
        elif args.action == 'import':
            if not args.json_file:
                print("错误：导入操作需要 --json-file 参数")
                sys.exit(1)
            result = writer.import_from_json(
                args.spreadsheet_token, args.sheet_id, args.json_file, args.clear_existing
            )
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if not result.get('success'):
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({
            "success": False,
            "message": "操作失败",
            "error": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
