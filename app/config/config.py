from pathlib import Path
from dotenv import load_dotenv
from app.utils.logger import get_logger
import os

class Config:
    _instance = None

    def __new__(cls, env_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            if env_path is None:
                get_logger().info(f"Config initialized with env path {env_path}")
                base_dir = Path(__file__).resolve().parent
                env_path = base_dir / ".env"
            load_dotenv(env_path)

            cls._instance.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
            cls._instance.HOST = os.getenv("HOST", "127.0.0.1")
            cls._instance.PORT = int(os.getenv("PORT", 8000))
            # cls._instance.DB_URL = os.getenv("DB_URL", "sqlite:///./default.db")
        return cls._instance

config = Config()