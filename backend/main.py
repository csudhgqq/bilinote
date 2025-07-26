import os
from contextlib import asynccontextmanager
import time
import json
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from dotenv import load_dotenv

from app.db.init_db import init_db
from app.db.provider_dao import seed_default_providers
from app.exceptions.exception_handlers import register_exception_handlers
# from app.db.model_dao import init_model_table
# from app.db.provider_dao import init_provider_table
from app.utils.logger import get_logger
from app import create_app
from app.transcriber.transcriber_provider import get_transcriber
from events import register_handler
from ffmpeg_helper import ensure_ffmpeg_or_raise

logger = get_logger(__name__)
load_dotenv()

# 请求响应日志中间件
class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 读取请求体
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                # 重新设置请求体，以便后续处理能正常读取
                async def new_receive():
                    return {"type": "http.request", "body": body}
                request._receive = new_receive
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")
        
        # 记录请求信息
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"=== API 请求开始 ===")
        logger.info(f"客户端IP: {client_ip}")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求路径: {request.url.path}")
        logger.info(f"查询参数: {dict(request.query_params)}")
        logger.info(f"请求头: {dict(request.headers)}")
        
        if body:
            try:
                # 尝试解析JSON body
                body_str = body.decode('utf-8')
                if body_str:
                    try:
                        body_json = json.loads(body_str)
                        logger.info(f"请求体 (JSON): {json.dumps(body_json, ensure_ascii=False, indent=2)}")
                    except json.JSONDecodeError:
                        logger.info(f"请求体 (文本): {body_str}")
                else:
                    logger.info("请求体: 空")
            except Exception as e:
                logger.warning(f"解析请求体时出错: {e}")
        
        try:
            # 处理请求
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"处理时间: {process_time:.4f}秒")
            
            # 如果是错误响应，记录更多信息
            if response.status_code >= 400:
                logger.error(f"API 调用出错 - 状态码: {response.status_code}")
                if hasattr(response, 'body'):
                    try:
                        # 读取响应体
                        response_body = b""
                        async for chunk in response.body_iterator:
                            response_body += chunk
                        
                        if response_body:
                            try:
                                response_json = json.loads(response_body.decode('utf-8'))
                                logger.error(f"错误响应体: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                            except:
                                logger.error(f"错误响应体 (文本): {response_body.decode('utf-8', errors='ignore')}")
                        
                        # 重新构造响应
                        return Response(
                            content=response_body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )
                    except Exception as e:
                        logger.error(f"读取错误响应体时出错: {e}")
            
            logger.info("=== API 请求结束 ===\n")
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            logger.error(f"=== API 请求异常 ===")
            logger.error(f"处理时间: {process_time:.4f}秒")
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常消息: {error_msg}")
            logger.error(f"完整堆栈:\n{stack_trace}")
            logger.error("=== API 请求异常结束 ===\n")
            
            # 返回500错误
            return JSONResponse(
                status_code=500,
                content={"detail": f"服务器内部错误: {error_msg}"}
            )

# 读取 .env 中的路径
static_path = os.getenv('STATIC', '/static')
out_dir = os.getenv('OUT_DIR', './static/screenshots')

# 自动创建本地目录（static 和 static/screenshots）
static_dir = "static"
uploads_dir = "uploads"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_handler()
    init_db()
    get_transcriber(transcriber_type=os.getenv("TRANSCRIBER_TYPE", "fast-whisper"))
    seed_default_providers()
    yield

app = create_app(lifespan=lifespan)

# 添加请求响应日志中间件
app.add_middleware(RequestResponseLoggingMiddleware)

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://tauri.localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #  加上 Tauri 的 origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.mount(static_path, StaticFiles(directory=static_dir), name="static")
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")









if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8483))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=False)