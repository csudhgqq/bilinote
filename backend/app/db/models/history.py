from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON
from sqlalchemy.orm import declarative_base

from app.db.engine import Base


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)  # PENDING, RUNNING, SUCCESS, FAILED
    platform = Column(String, nullable=False)
    
    # 音频元数据
    title = Column(String)
    cover_url = Column(String)
    duration = Column(Integer)
    file_path = Column(String)
    video_id = Column(String)
    raw_info = Column(JSON)
    
    # 转录数据
    transcript_full_text = Column(Text)
    transcript_language = Column(String)
    transcript_raw = Column(JSON)
    transcript_segments = Column(JSON)
    
    # 生成的笔记内容
    markdown_content = Column(Text)
    markdown_versions = Column(JSON)  # 存储多个版本的 markdown
    
    # 表单数据
    form_data = Column(JSON)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 