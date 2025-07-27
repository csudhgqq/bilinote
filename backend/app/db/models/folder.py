from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.engine import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(String, primary_key=True)  # 使用UUID字符串作为主键
    name = Column(String, nullable=False)
    parent_id = Column(String, ForeignKey('folders.id'), nullable=True)  # 父文件夹ID，NULL表示根目录
    is_expanded = Column(Boolean, default=True)  # 是否展开
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent")