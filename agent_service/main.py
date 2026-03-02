"""
Agent Service 主程序
提供代码执行API服务
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from executor import CodeExecutor
import uvicorn

app = FastAPI(title="Code Sandbox API", version="1.0.0")
executor = CodeExecutor()


class CodeRequest(BaseModel):
    """代码执行请求"""
    code: str
    timeout: int = None  # 可选，默认使用配置文件中的超时时间


class CodeResponse(BaseModel):
    """代码执行响应"""
    stdout: str
    stderr: str
    exit_code: int
    success: bool


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Code Sandbox API",
        "version": "1.0.0",
        "description": "Tool Calling 2.0 Agent 服务的 Python 代码执行环境"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/execute", response_model=CodeResponse)
async def execute_code(request: CodeRequest):
    """
    执行Python代码

    接收Python代码字符串，在安全的沙箱环境中执行，并返回执行结果。

    代码执行规则：
    - 工作目录：sandbox/workspace（严格限制）
    - skills目录：../skills（只读）
    - 环境变量：自动注入LARK_APP_ID等凭证
    - 超时时间：默认60秒
    - 安全限制：模块白名单、路径隔离
    """
    try:
        result = await executor.execute(
            request.code,
            timeout=request.timeout
        )
        return CodeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workspace-info")
async def workspace_info():
    """获取工作区信息"""
    return {
        "workspace_dir": str(executor.workspace_dir),
        "skills_dir": str(executor.skills_dir),
        "timeout": executor.timeout
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
