#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鑷姩鍖栨祴璇曞钩鍙?API 瀹㈡埛绔?
鏀寔鐢ㄤ緥鐩綍銆佺敤渚嬨€佹楠ょ殑瀹屾暣 CRUD 鎿嶄綔
"""

import requests
import json
import urllib3

# 绂佺敤 SSL 璀﹀憡锛堟祴璇曞钩鍙颁娇鐢ㄨ嚜绛惧悕璇佷功锛?
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PlatformClient:
    """鑷姩鍖栨祴璇曞钩鍙板鎴风"""

    def __init__(self, base_url, token, creator_name="System", creator_id="0"):
        """
        鍒濆鍖栧鎴风

        Args:
            base_url: 骞冲彴鍩虹URL锛屽 https://platform.example.com
            token: 璁块棶token
            creator_name: 鍒涘缓鑰呭悕绉?
            creator_id: 鍒涘缓鑰匢D
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.creator_name = creator_name
        self.creator_id = creator_id

        # 鍩虹璇锋眰澶?
        self.headers = {
            "token": self.token,
            "Content-Type": "application/json",
        }

    # ==================== 鐩綍鐩稿叧鎿嶄綔 ====================

    def create_directory(self, name, parent_id, note="", priority=2):
        """
        鍒涘缓鐢ㄤ緥鐩綍

        Args:
            name: 鐩綍鍚嶇О
            parent_id: 鐖剁洰褰旾D
            note: 鐩綍鎻忚堪
            priority: 浼樺厛绾?

        Returns:
            dict: {"success": bool, "data": dir_id, "message": str}
        """
        url = f"{self.base_url}/case"

        payload = {
            "productId": 1,
            "name": name,
            "priority": priority,
            "note": note,
            "caseType": 0,  # 0 浠ｈ〃鐩綍
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
                        "message": "鐩綍鍒涘缓鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鍒涘缓澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def update_directory(self, dir_id, name=None, note=None, priority=None):
        """
        鏇存柊鐢ㄤ緥鐩綍

        Args:
            dir_id: 鐩綍ID
            name: 鐩綍鍚嶇О锛堝彲閫夛級
            note: 鐩綍鎻忚堪锛堝彲閫夛級
            priority: 浼樺厛绾э紙鍙€夛級

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 骞冲彴涓嶆敮鎸?PUT /case/{id}锛岄渶鍏?GET 鑾峰彇瀹屾暣鏁版嵁鍐?POST /case锛堝甫 id 瀛楁锛?
        get_url = f"{self.base_url}/case/{dir_id}"
        post_url = f"{self.base_url}/case"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "鑾峰彇鐩綍璇︽儏澶辫触"}

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
                        "message": "鐩綍鏇存柊鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏇存柊澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def delete_directory(self, dir_id):
        """
        鍒犻櫎鐢ㄤ緥鐩綍

        Args:
            dir_id: 鐩綍ID

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
                        "message": "鐩綍鍒犻櫎鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '鍒犻櫎澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def get_directory(self, dir_id):
        """
        鏌ヨ鐢ㄤ緥鐩綍璇︽儏

        Args:
            dir_id: 鐩綍ID

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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def list_directories(self, parent_id=None):
        """
        鏌ヨ鐢ㄤ緥鐩綍鍒楄〃

        Args:
            parent_id: 鐖剁洰褰旾D锛堝彲閫夛級

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/case/list"

        params = {
            "caseType": 0,  # 0=鐩綍
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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def get_case_variables_v2(self, case_id):
        """
        鑾峰彇鐢ㄤ緥鍙橀噺鍒楄〃 (浣跨敤楠岃瘉鎴愬姛鐨?/case/variables/{id} 鎺ュ彛)
        """
        url = f"{self.base_url}/case/variables/{case_id}"
        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "message": f"HTTP閿欒: {resp.status_code}",
                    "raw": resp.text[:300]
                }

            try:
                return resp.json()
            except ValueError:
                return {
                    "success": False,
                    "message": "鍝嶅簲涓嶆槸鍚堟硶JSON",
                    "raw": resp.text[:300]
                }
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==================== 鐢ㄤ緥鐩稿叧鎿嶄綔 ====================

    def create_case(self, name, directory_id, description="", note="", priority=2, variables=None, request=None, check=None):
        """
        鍒涘缓鐢ㄤ緥

        Args:
            name: 鐢ㄤ緥鍚嶇О
            directory_id: 鎵€灞炵洰褰旾D
            description: 鐢ㄤ緥鎻忚堪
            note: 澶囨敞淇℃伅
            priority: 浼樺厛绾?
            variables: 鍙橀噺鍒楄〃 [{"name": "var1", "value": "val1"}]
            request: 璇锋眰淇℃伅 {"method": "POST", "url": "/api/test", "headers": {}, "body": {}}
            check: 鏍￠獙鍒楄〃 [{"expect": 200}]

        Returns:
            dict: {"success": bool, "data": case_id, "message": str}
        """
        # 鍏堝垱寤虹敤渚嬪熀纭€淇℃伅
        url = f"{self.base_url}/case"

        payload = {
            "productId": 1,
            "name": name,
            "priority": priority,
            "note": note,
            "caseType": 2,  # 2 浠ｈ〃鑷姩鍖栫敤渚?
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

                    # 鍒涘缓鍙橀噺
                    if variables:
                        self._create_variables(case_id, variables)

                    # 鍒涘缓姝ラ
                    if request:
                        self._create_step(case_id, name, request, check or [])

                    return {
                        "success": True,
                        "data": case_id,
                        "message": "鐢ㄤ緥鍒涘缓鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鍒涘缓澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def update_case(self, case_id, name=None, description=None, note=None, priority=None):
        """
        鏇存柊鐢ㄤ緥

        Args:
            case_id: 鐢ㄤ緥ID
            name: 鐢ㄤ緥鍚嶇О锛堝彲閫夛級
            description: 鐢ㄤ緥鎻忚堪锛堝彲閫夛級
            note: 澶囨敞淇℃伅锛堝彲閫夛級
            priority: 浼樺厛绾э紙鍙€夛級

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 骞冲彴涓嶆敮鎸?PUT /case/{id}锛岄渶鍏?GET 鑾峰彇瀹屾暣鏁版嵁鍐?POST /case锛堝甫 id 瀛楁锛?
        get_url = f"{self.base_url}/case/{case_id}"
        post_url = f"{self.base_url}/case"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "鑾峰彇鐢ㄤ緥璇︽儏澶辫触"}

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
                        "message": "鐢ㄤ緥鏇存柊鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏇存柊澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def delete_case(self, case_id):
        """
        鍒犻櫎鐢ㄤ緥

        Args:
            case_id: 鐢ㄤ緥ID

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
                        "message": "鐢ㄤ緥鍒犻櫎鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '鍒犻櫎澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def get_cases_children(self, case_id):
        """
        鎸夌収鐖剁洰褰曢亶鍘嗗瓙鑺傜偣锛堢敤渚嬶級
        瀵瑰簲鎺ュ彛: GET /cases/children/{caseId}
        
        Args:
            case_id: 鐖剁洰褰旾D (濡?51399)
            
        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        # 娉ㄦ剰锛氱敤鎴锋彁渚涚殑鎺ュ彛璺緞鍙兘涓嶅甫 /api/sdet-atp锛屾牴鎹熀纭€URL鑷€傚簲
        url = f"{self.base_url}/cases/children/{case_id}"
        
        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "query children success"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', 'query children failed')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def get_case(self, case_id):
        """
        鏌ヨ鐢ㄤ緥璇︽儏

        Args:
            case_id: 鐢ㄤ緥ID

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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def list_cases(self, directory_id=None):
        """
        鏌ヨ鐢ㄤ緥鍒楄〃

        Args:
            directory_id: 鐩綍ID锛堝彲閫夛級

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        url = f"{self.base_url}/case/list"

        params = {
            "caseType": 2,  # 2=鑷姩鍖栫敤渚?
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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    # ==================== 姝ラ鐩稿叧鎿嶄綔 ====================

    def _create_step(self, case_id, name, request, check):
        """
        鍐呴儴鏂规硶锛氬垱寤烘楠?

        Args:
            case_id: 鐢ㄤ緥ID
            name: 姝ラ鍚嶇О
            request: 璇锋眰淇℃伅
            check: 鏍￠獙鍒楄〃

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
                        "message": "姝ラ鍒涘缓鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鍒涘缓澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def create_step(self, case_id, name, order, host="${G_host}", protocol=0, path="", method=1,
                    headers=None, body=None, params=None, variables=None, check=None, type=0, quote_id=None):
        """
        鍒涘缓鐢ㄤ緥姝ラ

        Args:
            case_id: 鐢ㄤ緥ID
            name: 姝ラ鍚嶇О
            order: 姝ラ椤哄簭
            host: 涓绘満鍦板潃
            protocol: 鍗忚 0=HTTP, 1=HTTPS
            path: 璇锋眰璺緞
            method: 璇锋眰鏂规硶(鏁存暟: 0=GET, 1=POST, 2=PUT, 3=DELETE)
            headers: 璇锋眰澶?
            body: 璇锋眰浣?
            params: 璇锋眰鍙傛暟
            variables: 姝ラ鍙橀噺
            check: 鏍￠獙鍒楄〃
            type: 姝ラ绫诲瀷(0=鏅€氭楠? 1=寮曠敤鐢ㄤ緥)
            quote_id: 寮曠敤鐨勫叕鍏辩敤渚婭D (褰搕ype=1鏃跺繀濉?

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
                        "message": "姝ラ鍒涘缓鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鍒涘缓澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def update_step(self, step_id, **kwargs):
        """
        鏇存柊鐢ㄤ緥姝ラ

        Args:
            step_id: 姝ラID
            **kwargs: 瑕佹洿鏂扮殑瀛楁

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        # 骞冲彴涓嶆敮鎸?PUT/POST /flow/{id}锛岄渶鍏?GET 鑾峰彇瀹屾暣鏁版嵁鍐?POST /flow锛堝甫 id 瀛楁锛?
        get_url = f"{self.base_url}/flow/{step_id}"
        post_url = f"{self.base_url}/flow"

        try:
            get_resp = requests.get(get_url, headers=self.headers, verify=False)
            if get_resp.status_code != 200 or not get_resp.json().get("success"):
                return {"success": False, "data": None, "message": "鑾峰彇姝ラ璇︽儏澶辫触"}

            detail = get_resp.json()["data"]
            detail["modifier"] = self.creator_name
            detail["modifierId"] = self.creator_id

            # 鏇存柊鎸囧畾瀛楁
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
                        "message": "姝ラ鏇存柊鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏇存柊澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def delete_step(self, step_id):
        """
        鍒犻櫎鐢ㄤ緥姝ラ

        Args:
            step_id: 姝ラID

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
                        "message": "姝ラ鍒犻櫎鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '鍒犻櫎澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def get_step(self, step_id):
        """
        鏌ヨ鐢ㄤ緥姝ラ璇︽儏

        Args:
            step_id: 姝ラID

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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def list_steps(self, case_id):
        """
        鏌ヨ鐢ㄤ緥姝ラ鍒楄〃

        Args:
            case_id: 鐢ㄤ緥ID

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
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    # ==================== 鍙橀噺鐩稿叧鎿嶄綔 ====================

    def _create_variables(self, case_id, variables):
        """
        鍐呴儴鏂规硶锛氭壒閲忓垱寤哄彉閲?

        Args:
            case_id: 鐢ㄤ緥ID
            variables: 鍙橀噺鍒楄〃 [{"name": "var1", "value": "val1"}]
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
        鍒涘缓鐢ㄤ緥鍙橀噺

        Args:
            case_id: 鐢ㄤ緥ID
            name: 鍙橀噺鍚?
            value: 鍙橀噺鍊?

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
                        "message": "鍙橀噺鍒涘缓鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": res_json.get('resMessage', '鍒涘缓澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def update_variable(self, var_id, value=None, case_id=None, name=None, note=None):
        """
        鏇存柊鐢ㄤ緥鍙橀噺锛堝吋瀹瑰钩鍙板綋鍓嶆纭ā寮忥細POST /case/variable锛宐ody 蹇呴』甯?id锛?

        Args:
            var_id: 鍙橀噺ID
            value: 鍙橀噺鍊硷紙鍙€夛級
            case_id: 鐢ㄤ緥ID锛堟帹鑽愪紶鍏ワ級
            name: 鍙橀噺鍚嶏紙鎺ㄨ崘浼犲叆锛?
            note: 鍙橀噺澶囨敞锛堝彲閫夛級

        Returns:
            dict: {"success": bool, "data": dict, "message": str}
        """
        url = f"{self.base_url}/case/variable"

        payload = {
            "id": var_id
        }
        if case_id is not None:
            payload["caseId"] = case_id
        if name is not None:
            payload["name"] = name
        if value is not None:
            payload["value"] = value
        if note is not None:
            payload["note"] = note

        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data"),
                        "message": "鍙橀噺鏇存柊鎴愬姛"
                    }
                return {
                    "success": False,
                    "data": None,
                    "message": res_json.get('resMessage', '鏇存柊澶辫触')
                }
            return {
                "success": False,
                "data": None,
                "message": f"HTTP閿欒: {resp.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def delete_variable(self, var_id):
        """
        鍒犻櫎鐢ㄤ緥鍙橀噺

        Args:
            var_id: 鍙橀噺ID

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
                        "message": "鍙橀噺鍒犻櫎鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "message": res_json.get('resMessage', '鍒犻櫎澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

    def list_variables(self, case_id):
        """
        鏌ヨ鐢ㄤ緥鍙橀噺鍒楄〃

        Args:
            case_id: 鐢ㄤ緥ID

        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        # 骞冲彴绋冲畾鎺ュ彛锛欸ET /case/variables/{case_id}
        url = f"{self.base_url}/case/variables/{case_id}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("success"):
                    return {
                        "success": True,
                        "data": res_json.get("data", []),
                        "message": "鏌ヨ鎴愬姛"
                    }
                else:
                    return {
                        "success": False,
                        "data": [],
                        "message": res_json.get('resMessage', '鏌ヨ澶辫触')
                    }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"HTTP閿欒: {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"璇锋眰寮傚父: {str(e)}"
            }

