import logging
import sys
from pathlib import Path
from datetime import datetime

def get_logger(name: str = "backend", log_dir: Path = None) -> logging.Logger:
    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "\033[92m[%(asctime)s]\033[0m [%(levelname)s] %(name)s: %(message)s",
        "%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Logger '{name}' initialized. Writing logs to {log_file}")
    return logger
