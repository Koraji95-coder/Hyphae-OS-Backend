import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
from fastapi import Request
from backend.app.shared.state.session_manager import session

# 🛡️ Safe formatter to prevent logging errors from missing fields (e.g., user, device_id)
class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'user'):
            record.user = 'N/A'
        if not hasattr(record, 'device_id'):
            record.device_id = 'N/A'
        return super().format(record)

# 🧠 Context filter adds user/session info to every log automatically
class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.user = session.get_user_name() or "N/A"
        record.device_id = session.get_flag("device_id") or "N/A"
        return True

# 🛠️ Initialize structured logging with rotation and session metadata
def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    app_name: str = "hyphaeos"
) -> None:
    """
    Set up logging with both console + rotating file outputs.
    - Includes dynamic session context (user/device_id)
    - Uses custom format with timestamp, log level, etc.
    """
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{log_dir}/{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
    agent_logger = logging.getLogger("agent.sporelink")
    agent_logger.setLevel(logging.INFO)
    agent_handler = RotatingFileHandler("logs/agent/sporelink_20240527.log")
    agent_logger.addHandler(agent_handler)
        

    formatter = SafeFormatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] '
        '(user=%(user)s device=%(device_id)s) %(message)s'
    )
    
    # --- Agent log rotation ---
    agent_names = ['sporelink', 'neuroweave', 'rootbloom', 'system']
    for agent in agent_names:
        os.makedirs(f"{log_dir}/agents", exist_ok=True)
        agent_log_path = f"{log_dir}/agents/{agent}_{log_date}.log"
        handler = logging.handlers.RotatingFileHandler(
            agent_log_path, maxBytes=10 * 1024 * 1024, backupCount=10
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger(f"agent.{agent}")
        logger.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(handler)

    # 🔁 Rotating file handler (keeps 10x 10MB logs)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)

    # 🖥️ Output logs to console as well
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 🧩 Set root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 🧠 Add user/device context into every log
    root_logger.addFilter(RequestContextFilter())

    # 📉 Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# 🔍 Enrich individual logs with HTTP context (method, path, IP)
def get_request_log_context(request: Optional[Request] = None) -> dict:
    """
    Build contextual metadata for logging a specific request.
    """
    context = {
        "user": session.get_user_name() or "N/A",
        "device_id": session.get_flag("device_id") or "N/A"
    }
    if request:
        context.update({
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host if request.client else None,
        })
    return context
