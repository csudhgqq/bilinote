import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# 默认 SQLite，如果想换 PostgreSQL 或 MySQL，可以直接改 .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bili_note.db")

# SQLite 需要特定连接参数，其他数据库不需要
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL 连接池配置
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20
    engine_args["pool_pre_ping"] = True
    engine_args["pool_recycle"] = 3600

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    **engine_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_engine():
    return engine


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()