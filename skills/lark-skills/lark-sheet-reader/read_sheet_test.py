import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lark_sheet_reader import LarkSheetReader
import json

# 配置
config = {
    "app_id": "cli_a83faf50a228900e",
    "app_secret": "VN9qcmCuJhMgG39Hs5nT1fcDUPsywWoH"
}

# URL
url = "https://ruijie.feishu.cn/sheets/K8V2sTKLyhE54Ot75EycbnKLnvb?sheet=FYZ5JP"

try:
    # 初始化读取器
    reader = LarkSheetReader(**config)
    
    # 从URL读取表格
    data = reader.read_from_url(url)
    
    # 只读取前10行数据（包括表头）
    if len(data) > 10:
        data = data[:10]
    
    # 输出JSON
    print("表格数据（前10行）：")
    print("=" * 80)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("=" * 80)
    print(f"\n共读取 {len(data)} 行数据")
    
except Exception as e:
    print(f"读取失败: {e}")
    import traceback
    traceback.print_exc()
