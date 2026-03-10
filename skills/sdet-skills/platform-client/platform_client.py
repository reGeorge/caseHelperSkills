#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化测试平台 API 客户端
支持用例目录、用例、步骤的完整 CRUD 操作
"""

import requests
import json
import urllib3

# 禁用 SSL 警告（测试平台使用自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PlatformClient:
    """自动化测试平台客户端"""

    def __init__(self, base_url, token, creator_name="System", creator_id="0"):
        """
        初始化客户端

        Args:
            base_url: 平台基础URL，如 https://platform.example.com
            token: 访问token
            creator_name: 创建者名称
            creator_id: 创建者ID
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.creator_name = creator_name
        self.creator_id = creator_id

        # 基础请求头
        self.headers = {
            "token": self.token,
            "Content-Type": "application/json",
        }

    # ==================== 目录相关操作 ====================

    def create_directory(self, name, parent_id, note="", priority=2):
        """
        创建用例目录

        Args:
            name: 目录名称
            parent_id: 父目录ID
            note: 目录描述
            priority: 优先级

        Returns:
            dict: {"success": bool, "data": dir_id, "message": str}
        """
        url = f"{self.base_url}/case"

        payload = {
            "productId": 1,
            "name": name,
            "priority": priority,
            "note": note,
            "caseType": 0,  # 0 代表目录
            "parent": parent_id,
            "creator": self.creator_name,
            "creatorId": self.creator_id,
            "modifier": self.creator_name,
            "modifierId": self.creator_id,
            "status": 0,
            "deleted": 0
        }

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "目录创建成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '创建失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def update_directory(self, dir_id, name=None, note=None, priority=None):
        """
        更新用例目录

        Args:
            dir_id: 目录ID
            name: 目录名称（可选）
            note: 目录描述（可选）
            priority: 优先级（可选）

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 平台不支持 PUT /case/{id}，需先 GET 获取完整数据再 POST /case（带 id 字段）
        get_url = f"{self.base_url}/case/{dir_id}"
        post_url = f"{self.base_url}/case"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "获取目录详情失败"}

            detail = get_resp.json()["data"]
            detail["modifier"] = self.creator_name
            detail["modifierId"] = self.creator_id

            if name is not None:
                detail["name"] = name
            if note is not None:
                detail["note"] = note
            if priority is not None:
                detail["priority"] = priority

            resp = requests.post(post_url, headers=self.headers, json=detail, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "目录更新成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '更新失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def delete_directory(self, dir_id):
        """
        删除用例目录

        Args:
            dir_id: 目录ID

        Returns:
            dict: {"success": bool, "message": str}
        """
        url = f"{self.base_url}/case/{dir_id}"

        try:
            resp = requests.delete(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "message": "目录删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '删除失败')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求异常: {str(e)}"
            }

    def get_directory(self, dir_id):
        """
        查询用例目录详情

        Args:
            dir_id: 目录ID

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        url = f"{self.base_url}/case/{dir_id}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def list_directories(self, parent_id=None):
        """
        查询用例目录列表

        Args:
            parent_id: 父目录ID（可选）

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/case/list"

        params = {
            "caseType": 0,  # 0=目录
        }

        if parent_id is not None:
            params["parent"] = parent_id

        try:
            resp = requests.get(url, headers=self.headers, params=params, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"请求异常: {str(e)}"
            }

    def update_variable(self, variable_id, case_id, name, value):
        """
        更新用例变量 (基于用户抓包分析的正确传参方式)

        Args:
            variable_id: 变量ID
            case_id: 用例ID
            name: 变量名称
            value: 变量值

        Returns:
            dict: {"success": bool, "message": str}
        """
        url = f"{self.base_url}/case/variable"
        payload = {
            "caseId": case_id,
            "name": name,
            "id": variable_id,
            "value": value
        }

        try:
            # 经测试，ATP 平台更新变量需使用 POST 且 payload 包含 id
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            res_json = resp.json()
            if res_json.get("success"):
                return {"success": True, "message": "变量更新成功"}
            else:
                return {"success": False, "message": res_json.get('resMessage', '更新失败')}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}"}

    def get_case_variables_v2(self, case_id):
        """
        获取用例变量列表 (使用验证成功的 /case/variables/{id} 接口)
        """
        url = f"{self.base_url}/case/variables/{case_id}"
        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            return resp.json()
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==================== 用例相关操作 ====================

    def create_case(self, name, directory_id, description="", note="", priority=2, variables=None, request=None, check=None):
        """
        创建用例

        Args:
            name: 用例名称
            directory_id: 所属目录ID
            description: 用例描述
            note: 备注信息
            priority: 优先级
            variables: 变量列表 [{"name": "var1", "value": "val1"}]
            request: 请求信息 {"method": "POST", "url": "/api/test", "headers": {}, "body": {}}
            check: 校验列表 [{"expect": 200}]

        Returns:
            dict: {"success": bool, "data": case_id, "message": str}
        """
        # 先创建用例基础信息
        url = f"{self.base_url}/case"

        payload = {
            "productId": 1,
            "name": name,
            "priority": priority,
            "note": note,
            "caseType": 2,  # 2 代表自动化用例
            "parent": directory_id,
            "creator": self.creator_name,
            "creatorId": self.creator_id,
            "modifier": self.creator_name,
            "modifierId": self.creator_id,
            "status": 0,
            "deleted": 0
        }

        if description:
            payload["description"] = description

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    case_id = res_json.get("data")

                    # 创建变量
                    if variables:
                        self._create_variables(case_id, variables)

                    # 创建步骤
                    if request:
                        self._create_step(case_id, name, request, check or [])

                    return {
                        "success": True,
                        "data": case_id,
                        "message": "用例创建成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '创建失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def update_case(self, case_id, name=None, description=None, note=None, priority=None):
        """
        更新用例

        Args:
            case_id: 用例ID
            name: 用例名称（可选）
            description: 用例描述（可选）
            note: 备注信息（可选）
            priority: 优先级（可选）

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 平台不支持 PUT /case/{id}，需先 GET 获取完整数据再 POST /case（带 id 字段）
        get_url = f"{self.base_url}/case/{case_id}"
        post_url = f"{self.base_url}/case"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "获取用例详情失败"}

            detail = get_resp.json()["data"]
            detail["modifier"] = self.creator_name
            detail["modifierId"] = self.creator_id

            if name is not None:
                detail["name"] = name
            if description is not None:
                detail["description"] = description
            if note is not None:
                detail["note"] = note
            if priority is not None:
                detail["priority"] = priority

            resp = requests.post(post_url, headers=self.headers, json=detail, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "用例更新成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '更新失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def delete_case(self, case_id):
        """
        删除用例

        Args:
            case_id: 用例ID

        Returns:
            dict: {"success": bool, "message": str}
        """
        url = f"{self.base_url}/case/{case_id}"

        try:
            resp = requests.delete(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "message": "用例删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '删除失败')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求异常: {str(e)}"
            }

    def get_cases_children(self, case_id):
        """
        按照父目录遍历子节点（用例）
        对应接口: GET /cases/children/{caseId}
        
        Args:
            case_id: 父目录ID (如 51399)
            
        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        # 注意：用户提供的接口路径可能不带 /api/sdet-atp，根据基础URL自适应
        url = f"{self.base_url}/cases/children/{case_id}"
        
        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "查询子节点成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '查询子节点失败')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"请求异常: {str(e)}"
            }

    def get_case(self, case_id):
        """
        查询用例详情

        Args:
            case_id: 用例ID

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        url = f"{self.base_url}/case/{case_id}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def list_cases(self, directory_id=None):
        """
        查询用例列表

        Args:
            directory_id: 目录ID（可选）

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/case/list"

        params = {
            "caseType": 2,  # 2=自动化用例
        }

        if directory_id is not None:
            params["parent"] = directory_id

        try:
            resp = requests.get(url, headers=self.headers, params=params, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"请求异常: {str(e)}"
            }

    # ==================== 步骤相关操作 ====================

    def _create_step(self, case_id, name, request, check):
        """
        内部方法：创建步骤

        Args:
            case_id: 用例ID
            name: 步骤名称
            request: 请求信息
            check: 校验列表

        Returns:
            dict: {"success": bool, "data": step_id, "message": str}
        """
        url = f"{self.base_url}/flow"

        payload = {
            "caseId": case_id,
            "name": name,
            "order": 1,
            "host": "${G_host}",
            "protocol": 0,  # 0=HTTP
            "path": request.get("url", ""),
            "method": request.get("method", "POST"),
            "headers": request.get("headers", {}),
            "body": json.dumps(request.get("body", {})),
            "params": [],
            "variables": [],
            "check": check,
            "status": 0,
            "deleted": 0,
            "exception": 1,
            "responseTime": 0,
            "note": "",
            "creator": self.creator_name,
            "creatorId": self.creator_id,
            "modifier": self.creator_name,
            "modifierId": self.creator_id
        }

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "步骤创建成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '创建失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def create_step(self, case_id, name, order, host="${G_host}", protocol=0, path="", method=1,
                    headers=None, body=None, params=None, variables=None, check=None, type=0, quote_id=None):
        """
        创建用例步骤

        Args:
            case_id: 用例ID
            name: 步骤名称
            order: 步骤顺序
            host: 主机地址
            protocol: 协议 0=HTTP, 1=HTTPS
            path: 请求路径
            method: 请求方法(整数: 0=GET, 1=POST, 2=PUT, 3=DELETE)
            headers: 请求头
            body: 请求体
            params: 请求参数
            variables: 步骤变量
            check: 校验列表
            type: 步骤类型(0=普通步骤, 1=引用用例)
            quote_id: 引用的公共用例ID (当type=1时必填)

        Returns:
            dict: {"success": bool, "data": step_id, "message": str}
        """
        url = f"{self.base_url}/flow"

        payload = {
            "caseId": case_id,
            "name": name,
            "order": order,
            "host": host,
            "protocol": protocol,
            "path": path,
            "method": method,
            "headers": headers if headers is not None else [],
            "body": json.dumps(body) if body is not None else "{}",
            "params": params or [],
            "variables": variables or [],
            "check": check or [],
            "status": 0,
            "deleted": 0,
            "exception": 1,
            "type": type,
            "responseTime": 0,
            "note": "",
            "creator": self.creator_name,
            "creatorId": self.creator_id,
            "modifier": self.creator_name,
            "modifierId": self.creator_id
        }
        
        if quote_id is not None:
            payload["quoteId"] = quote_id

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "步骤创建成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '创建失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def update_step(self, step_id, **kwargs):
        """
        更新用例步骤

        Args:
            step_id: 步骤ID
            **kwargs: 要更新的字段

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 平台不支持 PUT/POST /flow/{id}，需先 GET 获取完整数据再 POST /flow（带 id 字段）
        get_url = f"{self.base_url}/flow/{step_id}"
        post_url = f"{self.base_url}/flow"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "获取步骤详情失败"}

            detail = get_resp.json()["data"]
            detail["modifier"] = self.creator_name
            detail["modifierId"] = self.creator_id

            # 更新指定字段
            for field in ['name', 'order', 'host', 'protocol', 'path', 'method',
                          'headers', 'body', 'params', 'variables', 'check', 'note']:
                if field in kwargs:
                    if field == 'body' and kwargs[field]:
                        detail[field] = json.dumps(kwargs[field])
                    else:
                        detail[field] = kwargs[field]

            resp = requests.post(post_url, headers=self.headers, json=detail, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "步骤更新成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '更新失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def delete_step(self, step_id):
        """
        删除用例步骤

        Args:
            step_id: 步骤ID

        Returns:
            dict: {"success": bool, "message": str}
        """
        url = f"{self.base_url}/flow/{step_id}"

        try:
            resp = requests.delete(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "message": "步骤删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '删除失败')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求异常: {str(e)}"
            }

    def get_step(self, step_id):
        """
        查询用例步骤详情

        Args:
            step_id: 步骤ID

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        url = f"{self.base_url}/flow/{step_id}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def list_steps(self, case_id):
        """
        查询用例步骤列表

        Args:
            case_id: 用例ID

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/flows/{case_id}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"请求异常: {str(e)}"
            }

    # ==================== 变量相关操作 ====================

    def _create_variables(self, case_id, variables):
        """
        内部方法：批量创建变量

        Args:
            case_id: 用例ID
            variables: 变量列表 [{"name": "var1", "value": "val1"}]
        """
        url = f"{self.base_url}/case/variable"

        for var in variables:
            try:
                requests.post(url, headers=self.headers, json={
                    "caseId": case_id,
                    "name": var.get("name"),
                    "value": var.get("value")
                }, verify=False)
            except Exception as e:
                pass

    def create_variable(self, case_id, name, value):
        """
        创建用例变量

        Args:
            case_id: 用例ID
            name: 变量名
            value: 变量值

        Returns:
            dict: {"success": bool, "data": var_id, "message": str}
        """
        url = f"{self.base_url}/case/variable"

        payload = {
            "caseId": case_id,
            "name": name,
            "value": value
        }

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "变量创建成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '创建失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def update_variable(self, var_id, value):
        """
        更新用例变量

        Args:
            var_id: 变量ID
            value: 变量值

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        url = f"{self.base_url}/case/variable/{var_id}"

        payload = {
            "value": value
        }

        try:
            resp = requests.put(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "变量更新成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '更新失败')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"请求异常: {str(e)}"
            }

    def delete_variable(self, var_id):
        """
        删除用例变量

        Args:
            var_id: 变量ID

        Returns:
            dict: {"success": bool, "message": str}
        """
        url = f"{self.base_url}/case/variable/{var_id}"

        try:
            resp = requests.delete(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "message": "变量删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '删除失败')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求异常: {str(e)}"
            }

    def list_variables(self, case_id):
        """
        查询用例变量列表

        Args:
            case_id: 用例ID

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/case/variable/list"

        params = {
            "caseId": case_id
        }

        try:
            resp = requests.get(url, headers=self.headers, params=params, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "查询成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '查询失败')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP错误: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"请求异常: {str(e)}"
            }
