import os
from dotenv import load_dotenv

# Load .env file from the backend directory relative to config.py
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

# Database Config
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "bhashashield")

# Construct MySQL Database URL
MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# SQLite Fallback URL
SQLITE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bhashashield.db"))
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# AI Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "xlm-roberta-base")
USE_TRANSFORMERS = os.getenv("USE_TRANSFORMERS", "true").lower() == "true"

# App Info
PROJECT_NAME = "Lang Detect AI"
VERSION = "1.0.0"
API_PREFIX = "/api"
