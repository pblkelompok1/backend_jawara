from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    logger.remove()  # remove default handler

    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | {message}",
        level="INFO",
    )

    # Rotating file logging
    logger.add(
        LOG_DIR / "app.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )

    return logger
