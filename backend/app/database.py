import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import pymysql

from app import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bhashashield.database")

Base = declarative_base()
engine = None
SessionLocal = None

def init_mysql_db():
    """Attempt to create the MySQL database if it does not exist."""
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            port=int(config.MYSQL_PORT)
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB}")
        connection.commit()
        connection.close()
        logger.info(f"MySQL database '{config.MYSQL_DB}' checked/created successfully.")
        return True
    except Exception as e:
        logger.warning(f"Could not initialize MySQL database directly: {e}")
        return False

def establish_connection():
    global engine, SessionLocal
    
    # Try MySQL first
    if init_mysql_db():
        try:
            logger.info("Connecting to MySQL...")
            engine = create_engine(
                config.MYSQL_URL, 
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5}
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("Successfully connected to MySQL database.")
            return "MySQL"
        except (OperationalError, Exception) as e:
            logger.warning(f"MySQL connection failed: {e}. Falling back to SQLite.")
            
    # Fallback to SQLite
    logger.info(f"Connecting to SQLite database at: {config.SQLITE_DB_PATH}")
    # For SQLite, we might need connect_args={"check_same_thread": False}
    engine = create_engine(
        config.SQLITE_URL, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Successfully connected to SQLite database.")
    return "SQLite"

# Run database setup
db_type = establish_connection()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
