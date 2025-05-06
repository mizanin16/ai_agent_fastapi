import os
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def get_logger_for_date():
    log_dir = "logs/requests"
    os.makedirs(log_dir, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filepath = os.path.join(log_dir, f"{date_str}.log")

    logger = logging.getLogger(f"request_logger_{date_str}")
    if not logger.handlers:
        handler = logging.FileHandler(filepath)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = get_logger_for_date()
        method = request.method
        path = request.url.path
        query = str(request.query_params)
        logger.info(f"{method} {path} | Query: {query}")
        return await call_next(request)
