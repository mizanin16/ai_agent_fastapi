import os
import logging

from fastapi import APIRouter
from datetime import datetime
from models.schemas import AgentErrorLog
router = APIRouter()


@router.post("/agent-log-error", status_code=204)
async def log_agent_error(log: AgentErrorLog):
    log_dir = "logs/errors"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"errors_{datetime.utcnow().strftime('%Y-%m-%d')}.log")

    logger = logging.getLogger("agent_error_logger")
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - ERROR - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)

    logger.error(f"Query: {log.query} | Error: {log.error} | Context: {log.context}")
    return
