import requests
import json
import urllib3
from config import config
from utils.logger import setup_logger

# 初始化 logger
logger = setup_logger('platform_skills')

# 禁用 SSL 警告（测试平台使用自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PlatformClient:
    def __init__(self):
        self.base_url = config.TEST_PLATFORM_URL
        self.headers = {
            "token": config.TEST_PLATFORM_TOKEN,  # 使用 token header 而不是 Authorization
            "Content-Type": "application/json",
        }

    def create_directory_if_not_exists(self, dir_name, parent_id=None):
        """
        创建目录
        parent_id: 如果不传，则使用 config 中的默认值
        """
        if parent_id is None:
            parent_id = config.DEFAULT_PARENT_ID

        url = f"{self.base_url}/case" # 注意：n8n中创建目录也是调用的 /case 接口，只是 caseType=0
        
        payload = {
            "productId": 1, # n8n中写死为1
            "name": dir_name,
            "priority": 2,
            "note": f"自动创建的目录: {dir_name}",
            "caseType": 0, # 0 代表目录
            "parent": parent_id,
            
            # 注入创建者信息
            "creator": config.CREATOR_NAME,
            "creatorId": config.CREATOR_ID,
            "modifier": config.CREATOR_NAME,
            "modifierId": config.CREATOR_ID,
            
            "status": 0,
            "deleted": 0
        }

        try:
            logger.info(f"正在创建目录: {dir_name} (父目录ID: {parent_id})")
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 这里简化逻辑：直接尝试创建。
            # 如果平台支持"如果存在则返回ID"，那最好。
            # 如果不支持，可能需要先调用 list 接口查询 (n8n逻辑里似乎直接创建或没体现查询)
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)

            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    dir_id = res_json.get("data")
                    logger.info(f"目录创建成功, ID: {dir_id}")
                    return dir_id
                else:
                    error_msg = res_json.get('resMessage', '未知错误')
                    logger.error(f"创建目录失败: {error_msg}")
                    return None
            else:
                logger.error(f"创建目录HTTP错误: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logger.error(f"请求平台异常: {e}", exc_info=True)
            return None

    def create_case(self, case_data, directory_id):
        """
        创建用例 (Case)
        """
        url = f"{self.base_url}/case"
        
        # 基础 payload 构造
        payload = {
            "productId": 1,
            "componentId": "",
            "name": case_data.get("name"),
            "priority": case_data.get("priority", 2),
            "note": case_data.get("description", ""),
            "caseType": 2, # 2 代表自动化用例 (根据 n8n 逻辑)
            "parent": directory_id,
            
            # 注入创建者信息
            "creator": config.CREATOR_NAME,
            "creatorId": config.CREATOR_ID,
            "modifier": config.CREATOR_NAME,
            "modifierId": config.CREATOR_ID,
            
            "status": 0,
            "deleted": 0
        }

        # 发送请求创建 Case
        try:
            logger.info(f"正在创建用例: {case_data.get('name')} (目录ID: {directory_id})")
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200 and resp.json().get("success"):
                case_id = resp.json().get("data")
                logger.info(f"用例创建成功, ID: {case_id}")
                
                # --- 关键：创建成功后，还需要创建 步骤(Steps) 和 变量(Variables) ---
                # n8n 逻辑中是 "准备创建步骤和变量的请求体" -> "创建自动化步骤和变量 http"
                self._create_steps_and_variables(case_id, case_data)
                
                return {"id": case_id, "status": "success"}
            else:
                error_msg = resp.text if resp.status_code != 200 else resp.json().get('resMessage', '未知错误')
                logger.error(f"用例创建失败: {error_msg}")
                return {"id": None, "status": "failed", "error": error_msg}
        except Exception as e:
            logger.error(f"用例创建异常: {e}", exc_info=True)
            return {"id": None, "status": "failed", "error": str(e)}

    def _create_steps_and_variables(self, case_id, case_data):
        """
        私有方法：在用例创建成功后，追加步骤和变量
        对应 n8n 中的 "创建自动化步骤和变量 http"
        """
        # 1. 创建变量
        if "variables" in case_data and case_data["variables"]:
            var_url = f"{self.base_url}/case/variable"
            logger.info(f"准备创建 {len(case_data['variables'])} 个变量")
            for var in case_data["variables"]:
                try:
                    resp = requests.post(var_url, headers=self.headers, json={
                        "caseId": case_id,
                        "name": var.get("name"),
                        "value": var.get("value")
                    }, verify=False)
                    if resp.status_code == 200:
                        logger.info(f"变量创建成功: {var.get('name')}")
                    else:
                        logger.warning(f"变量创建失败: {var.get('name')} - {resp.text}")
                except Exception as e:
                    logger.warning(f"变量创建异常: {var.get('name')} - {e}")

        # 2. 创建步骤 (Flows)
        if "request" in case_data: # 这是一个自动化用例，通常包含 request 信息
            step_url = f"{self.base_url}/flow"

            # 构造步骤 Payload (复刻 n8n 中 `准备创建步骤和变量的请求体` 的逻辑)
            step_payload = {
                "caseId": case_id,
                "name": case_data.get("name"), # 步骤名通常和用例名一致，或者是 "步骤1"
                "order": 1,
                "host": "${G_host}",
                "protocol": 0, # http
                "path": case_data["request"].get("url", ""),
                "method": case_data["request"].get("method", "POST"),
                "headers": case_data["request"].get("headers", {}),
                "body": json.dumps(case_data["request"].get("body", {})), # body 需转字符串
                "params": [], # 如果有 query params 需解析
                "variables": [], # 步骤级变量
                "check": case_data.get("check", []), # 直接使用原始的 check 字段
                "status": 0,
                "deleted": 0,
                "exception": 1,
                "responseTime": 0,
                "note": "",

                # 注入创建者
                "creator": config.CREATOR_NAME,
                "creatorId": config.CREATOR_ID,
                "modifier": config.CREATOR_NAME,
                "modifierId": config.CREATOR_ID
            }

            logger.info(f"准备创建步骤: {step_payload['name']}")
            logger.info(f"步骤请求数量: check={len(step_payload.get('check', []))}, variables={len(step_payload.get('variables', []))}")

            # 这里 n8n 是循环创建 steps，这里简化为创建一个主步骤
            try:
                logger.debug(f"步骤创建请求URL: {step_url}")
                logger.debug(f"步骤创建请求体: {json.dumps(step_payload, ensure_ascii=False)}")
                resp = requests.post(step_url, headers=self.headers, json=step_payload, verify=False)
                logger.info(f"步骤创建响应状态码: {resp.status_code}")
                logger.info(f"步骤创建响应内容: {resp.text}")
                
                if resp.status_code == 200:
                    resp_json = resp.json()
                    if resp_json.get("success"):
                        logger.info(f"步骤创建成功: {step_payload['name']}")
                    else:
                        logger.warning(f"步骤创建失败: {step_payload['name']} - {resp_json.get('resMessage', '未知错误')}")
                else:
                    logger.warning(f"步骤创建HTTP失败: {step_payload['name']} - 状态码={resp.status_code}, 响应={resp.text}")
            except Exception as e:
                logger.warning(f"步骤创建异常: {step_payload['name']} - {e}")

    # ==================== 查询操作 ====================
    
    def get_case_detail(self, case_id, use_v2=True):
        """
        查询用例详情
        
        Args:
            case_id: 用例ID
            use_v2: 是否使用v2版本接口（默认True）
        
        Returns:
            用例详情数据
        """
        if use_v2:
            url = f"{self.base_url}/case/v2/{case_id}"
        else:
            url = f"{self.base_url}/case/{case_id}"
        
        try:
            logger.info(f"查询用例详情: case_id={case_id}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    logger.info(f"用例详情查询成功")
                    return res_json.get("data")
                else:
                    logger.error(f"用例详情查询失败: {res_json.get('resMessage')}")
                    return None
            else:
                logger.error(f"用例详情查询HTTP错误: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"查询用例详情异常: {e}", exc_info=True)
            return None
    
    def get_case_flows(self, case_id):
        """
        查询用例步骤列表
        
        Args:
            case_id: 用例ID
        
        Returns:
            步骤列表
        """
        url = f"{self.base_url}/flows/{case_id}"
        
        try:
            logger.info(f"查询用例步骤列表: case_id={case_id}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    flows = res_json.get("data", [])
                    logger.info(f"步骤列表查询成功，共 {len(flows)} 个步骤")
                    return flows
                else:
                    logger.error(f"步骤列表查询失败: {res_json.get('resMessage')}")
                    return []
            else:
                logger.error(f"步骤列表查询HTTP错误: {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"查询步骤列表异常: {e}", exc_info=True)
            return []
    
    def get_case_variables(self, case_id):
        """
        查询用例变量列表
        
        Args:
            case_id: 用例ID
        
        Returns:
            变量列表
        """
        url = f"{self.base_url}/case/variables/{case_id}"
        
        try:
            logger.info(f"查询用例变量列表: case_id={case_id}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    variables = res_json.get("data", [])
                    logger.info(f"变量列表查询成功，共 {len(variables)} 个变量")
                    return variables
                else:
                    logger.error(f"变量列表查询失败: {res_json.get('resMessage')}")
                    return []
            else:
                logger.error(f"变量列表查询HTTP错误: {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"查询变量列表异常: {e}", exc_info=True)
            return []
    
    def get_case_list(self, parent_id, case_type=2):
        """
        查询用例列表
        
        Args:
            parent_id: 父目录ID
            case_type: 用例类型（2=自动化用例，0=目录）
        
        Returns:
            用例列表
        """
        url = f"{self.base_url}/case/list?parent={parent_id}&caseType={case_type}"
        
        try:
            logger.info(f"查询用例列表: parent_id={parent_id}, case_type={case_type}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    cases = res_json.get("data", [])
                    logger.info(f"用例列表查询成功，共 {len(cases)} 个用例")
                    return cases
                else:
                    logger.error(f"用例列表查询失败: {res_json.get('resMessage')}")
                    return []
            else:
                logger.error(f"用例列表查询HTTP错误: {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"查询用例列表异常: {e}", exc_info=True)
            return []
    
    def get_flow_detail(self, flow_id):
        """
        查询步骤详情
        
        Args:
            flow_id: 步骤ID
        
        Returns:
            步骤详情
        """
        url = f"{self.base_url}/flow/{flow_id}"
        
        try:
            logger.info(f"查询步骤详情: flow_id={flow_id}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    logger.info(f"步骤详情查询成功")
                    return res_json.get("data")
                else:
                    logger.error(f"步骤详情查询失败: {res_json.get('resMessage')}")
                    return None
            else:
                logger.error(f"步骤详情查询HTTP错误: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"查询步骤详情异常: {e}", exc_info=True)
            return None

    # ==================== 执行操作 ====================
    
    def trigger_case_debug(self, case_id, env_id=93, flow_ids=None):
        """
        触发用例调试执行
        
        Args:
            case_id: 用例ID
            env_id: 环境ID（默认93）
            flow_ids: 指定执行的步骤ID列表（None表示执行全部）
        
        Returns:
            执行日志ID（用于查询执行结果）
        """
        url = f"{self.base_url}/case/debug"
        
        payload = {
            "caseId": case_id,
            "envId": env_id,
            "flowIds": flow_ids if flow_ids else [],
            "caseDefault": {"httpProtocol": 1}
        }
        
        try:
            logger.info(f"触发用例调试: case_id={case_id}, env_id={env_id}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    log_id = res_json.get("data")
                    logger.info(f"用例调试触发成功，执行日志ID: {log_id}")
                    return log_id
                else:
                    logger.error(f"用例调试触发失败: {res_json.get('resMessage')}")
                    return None
            else:
                logger.error(f"用例调试触发HTTP错误: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"触发用例调试异常: {e}", exc_info=True)
            return None
    
    def get_debug_logs(self, log_id):
        """
        查询用例执行结果
        
        Args:
            log_id: 执行日志ID
        
        Returns:
            执行结果详情
        """
        url = f"{self.base_url}/case/debug/logs/{log_id}"
        
        try:
            logger.info(f"查询执行结果: log_id={log_id}")
            resp = requests.get(url, headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    logger.info(f"执行结果查询成功")
                    return res_json.get("data")
                else:
                    logger.error(f"执行结果查询失败: {res_json.get('resMessage')}")
                    return None
            else:
                logger.error(f"执行结果查询HTTP错误: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"查询执行结果异常: {e}", exc_info=True)
            return None

    # ==================== 创建操作（增强） ====================
    
    def create_flow(self, case_id, flow_data):
        """
        创建步骤（支持普通HTTP步骤和公共步骤引用）
        
        Args:
            case_id: 用例ID
            flow_data: 步骤数据
                - type=0: 普通HTTP请求步骤
                - type=1: 公共步骤引用
        
        Returns:
            步骤ID
        """
        url = f"{self.base_url}/flow"
        
        # 基础字段
        payload = {
            "caseId": case_id,
            "status": 0,
            "deleted": 0,
            "creator": config.CREATOR_NAME,
            "creatorId": config.CREATOR_ID,
            "modifier": config.CREATOR_NAME,
            "modifierId": config.CREATOR_ID
        }
        
        # 根据类型构造不同的payload
        if flow_data.get("type") == 1:
            # 公共步骤引用
            payload.update({
                "type": "1",
                "quoteId": flow_data.get("quoteId"),
                "name": flow_data.get("name", ""),
                "exception": flow_data.get("exception", 0),
                "delayTime": flow_data.get("delayTime", 0)
            })
        else:
            # 普通HTTP请求步骤
            payload.update({
                "type": 0,
                "name": flow_data.get("name", ""),
                "order": flow_data.get("order", 1),
                "host": flow_data.get("host", "${G_host}"),
                "port": flow_data.get("port"),
                "protocol": flow_data.get("protocol", 0),
                "path": flow_data.get("path", ""),
                "method": flow_data.get("method", "POST"),
                "headers": flow_data.get("headers", []),
                "body": flow_data.get("body", "{}"),
                "params": flow_data.get("params", []),
                "variables": flow_data.get("variables", []),
                "check": flow_data.get("check", []),
                "exception": flow_data.get("exception", 1),
                "responseTime": 0,
                "note": flow_data.get("note", ""),
                "cookieClean": flow_data.get("cookieClean", 0),
                "delayTime": flow_data.get("delayTime", 0),
                "ipVersion": flow_data.get("ipVersion", 0)
            })
        
        try:
            step_type = "公共步骤引用" if flow_data.get("type") == 1 else "HTTP请求步骤"
            logger.info(f"创建步骤（{step_type}）: {payload.get('name')}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    flow_id = res_json.get("data")
                    logger.info(f"步骤创建成功，ID: {flow_id}")
                    return flow_id
                else:
                    logger.error(f"步骤创建失败: {res_json.get('resMessage')}")
                    return None
            else:
                logger.error(f"步骤创建HTTP错误: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"创建步骤异常: {e}", exc_info=True)
            return None

_client = PlatformClient()

def ensure_test_directory(name, parent_id=None):
    return _client.create_directory_if_not_exists(name, parent_id)

def sync_case_to_platform(case_info, directory_id):
    return _client.create_case(case_data=case_info, directory_id=directory_id)