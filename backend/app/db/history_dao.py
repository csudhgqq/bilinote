from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.history import History
from app.db.engine import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def insert_history(
    task_id: str,
    status: str,
    platform: str,
    title: Optional[str] = None,
    cover_url: Optional[str] = None,
    duration: Optional[int] = None,
    file_path: Optional[str] = None,
    video_id: Optional[str] = None,
    raw_info: Optional[Dict] = None,
    transcript_full_text: Optional[str] = None,
    transcript_language: Optional[str] = None,
    transcript_raw: Optional[Dict] = None,
    transcript_segments: Optional[List] = None,
    markdown_content: Optional[str] = None,
    markdown_versions: Optional[List] = None,
    form_data: Optional[Dict] = None
) -> Optional[History]:
    """插入新的历史记录"""
    db = next(get_db())
    try:
        history = History(
            task_id=task_id,
            status=status,
            platform=platform,
            title=title,
            cover_url=cover_url,
            duration=duration,
            file_path=file_path,
            video_id=video_id,
            raw_info=raw_info,
            transcript_full_text=transcript_full_text,
            transcript_language=transcript_language,
            transcript_raw=transcript_raw,
            transcript_segments=transcript_segments,
            markdown_content=markdown_content,
            markdown_versions=markdown_versions,
            form_data=form_data
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        logger.info(f"History record inserted successfully. task_id: {task_id}")
        return history
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert history record: {e}")
        return None
    finally:
        db.close()


def update_history(task_id: str, **kwargs) -> Optional[History]:
    """更新历史记录"""
    db = next(get_db())
    try:
        history = db.query(History).filter_by(task_id=task_id).first()
        if not history:
            logger.warning(f"History record not found for task_id: {task_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(history, key) and value is not None:
                setattr(history, key, value)
        
        db.commit()
        db.refresh(history)
        logger.info(f"History record updated successfully. task_id: {task_id}")
        return history
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update history record: {e}")
        return None
    finally:
        db.close()


def get_history_by_task_id(task_id: str) -> Optional[History]:
    """根据任务ID获取历史记录"""
    db = next(get_db())
    try:
        history = db.query(History).filter_by(task_id=task_id).first()
        if history:
            logger.info(f"History record found for task_id: {task_id}")
        else:
            logger.info(f"No history record found for task_id: {task_id}")
        return history
    except Exception as e:
        logger.error(f"Failed to get history by task_id: {e}")
        return None
    finally:
        db.close()


def get_all_history(limit: int = 100, offset: int = 0) -> List[History]:
    """获取所有历史记录，支持分页"""
    db = next(get_db())
    try:
        histories = (
            db.query(History)
            .order_by(History.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        logger.info(f"Retrieved {len(histories)} history records")
        return histories
    except Exception as e:
        logger.error(f"Failed to get all history: {e}")
        return []
    finally:
        db.close()


def delete_history(task_id: str) -> bool:
    """删除历史记录"""
    db = next(get_db())
    try:
        history = db.query(History).filter_by(task_id=task_id).first()
        if not history:
            logger.warning(f"History record not found for task_id: {task_id}")
            return False
        
        db.delete(history)
        db.commit()
        logger.info(f"History record deleted successfully. task_id: {task_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete history record: {e}")
        return False
    finally:
        db.close()


def get_history_by_video(video_id: str, platform: str) -> List[History]:
    """根据视频ID和平台获取历史记录"""
    db = next(get_db())
    try:
        histories = (
            db.query(History)
            .filter_by(video_id=video_id, platform=platform)
            .order_by(History.created_at.desc())
            .all()
        )
        logger.info(f"Found {len(histories)} history records for video_id: {video_id}, platform: {platform}")
        return histories
    except Exception as e:
        logger.error(f"Failed to get history by video: {e}")
        return []
    finally:
        db.close() 