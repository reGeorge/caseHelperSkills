// 查看用例步骤
curl 'https://sdet.ruishan.cc/ap/atp/apiCase/detail/66242' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://sdet.ruishan.cc/ap/atp/apiCase' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --insecure

// 查看用例步骤
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/51401' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://sdet.ruishan.cc/ap/atp/apiCase/detail/66242' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查看用例变量
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/variables/66242' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://sdet.ruishan.cc/ap/atp/apiCase/detail/66242' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

//触发用例执行
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/debug' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://sdet.ruishan.cc' \
  -H 'Referer: https://sdet.ruishan.cc/ap/atp/apiCase/detail/66242' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --data-raw '{"caseId":66242,"envId":93,"flowIds":[],"caseDefault":{"httpProtocol":1}}' \
  --insecure


// 查看执行结果
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/debug/logs/1101754' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://sdet.ruishan.cc/ap/atp/apiCase/detail/66242' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// ==================== 创建操作 ====================

// 创建目录 (caseType=0)
curl -X POST 'https://sdet.ruishan.cc/api/sdet-atp/case' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Content-Type: application/json' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --data-raw '{
    "productId": 1,
    "name": "测试目录名称",
    "priority": 2,
    "note": "目录描述",
    "caseType": 0,
    "parent": 66241,
    "creator": "测试人员",
    "creatorId": "12345",
    "modifier": "测试人员",
    "modifierId": "12345",
    "status": 0,
    "deleted": 0
  }' \
  --insecure

// 创建用例 (caseType=2)
curl -X POST 'https://sdet.ruishan.cc/api/sdet-atp/case' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Content-Type: application/json' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --data-raw '{
    "productId": 1,
    "name": "测试用例名称",
    "priority": 2,
    "note": "用例描述",
    "caseType": 2,
    "parent": 66241,
    "creator": "测试人员",
    "creatorId": "12345",
    "modifier": "测试人员",
    "modifierId": "12345",
    "status": 0,
    "deleted": 0
  }' \
  --insecure

// 创建步骤 (普通HTTP请求步骤)
curl -X POST 'https://sdet.ruishan.cc/api/sdet-atp/flow' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Content-Type: application/json' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --data-raw '{
    "caseId": 66242,
    "name": "步骤名称",
    "order": 1,
    "host": "${G_host}",
    "protocol": 0,
    "path": "/api/test",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": "{}",
    "params": [],
    "variables": [],
    "check": [],
    "status": 0,
    "deleted": 0,
    "exception": 1,
    "responseTime": 0,
    "note": "",
    "creator": "测试人员",
    "creatorId": "12345",
    "modifier": "测试人员",
    "modifierId": "12345"
  }' \
  --insecure

// 创建变量
curl -X POST 'https://sdet.ruishan.cc/api/sdet-atp/case/variable' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Content-Type: application/json' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --data-raw '{
    "caseId": 66242,
    "name": "变量名",
    "value": "变量值"
  }' \
  --insecure

// ==================== 查询操作 ====================

// 查询用例详情
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/66242' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查询用例列表 (根据parent ID)
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/list?parent=66241&caseType=2' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查询步骤列表
curl 'https://sdet.ruishan.cc/api/sdet-atp/flow/list?caseId=66242' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查询步骤详情
curl 'https://sdet.ruishan.cc/api/sdet-atp/flow/{flowId}' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查询变量列表
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/variable/list?caseId=66242' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// ==================== 公共步骤说明 ====================
// 注意：当前API暂不支持直接引用公共步骤(caseid=51401)
// 解决方案：
// 1. 先查询公共步骤的详细信息：GET /case/51401
// 2. 再查询该用例的步骤列表：GET /flow/list?caseId=51401
// 3. 将步骤复制到新创建的用例中

// 查询公共步骤用例详情
curl 'https://sdet.ruishan.cc/api/sdet-atp/case/51401' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure

// 查询公共步骤列表
curl 'https://sdet.ruishan.cc/api/sdet-atp/flow/list?caseId=51401' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'token: NDY7d2VpYmluOzE3NzI1MDc0ODAxNzQ7M2UwMTEzMGZjYWZmZjRkMDE1MTU5ZGNmYmE4OWY5OWJiNGUxNDMyZTY3NzAxNTIxMDJlNjVlOGZkNjIwMGUyMQ==' \
  --insecure