from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.folder import Folder
from app.db.engine import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def insert_folder(
    folder_id: str,
    name: str,
    parent_id: Optional[str] = None,
    is_expanded: bool = True
) -> Optional[Folder]:
    """插入新的文件夹"""
    db = next(get_db())
    try:
        folder = Folder(
            id=folder_id,
            name=name,
            parent_id=parent_id,
            is_expanded=is_expanded
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        logger.info(f"Folder inserted successfully. folder_id: {folder_id}")
        return folder
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert folder: {e}")
        return None
    finally:
        db.close()


def update_folder(folder_id: str, **kwargs) -> Optional[Folder]:
    """更新文件夹"""
    db = next(get_db())
    try:
        folder = db.query(Folder).filter_by(id=folder_id).first()
        if not folder:
            logger.warning(f"Folder not found for folder_id: {folder_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(folder, key) and value is not None:
                setattr(folder, key, value)
        
        db.commit()
        db.refresh(folder)
        logger.info(f"Folder updated successfully. folder_id: {folder_id}")
        return folder
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update folder: {e}")
        return None
    finally:
        db.close()


def get_folder_by_id(folder_id: str) -> Optional[Folder]:
    """根据ID获取文件夹"""
    db = next(get_db())
    try:
        folder = db.query(Folder).filter_by(id=folder_id).first()
        if folder:
            logger.info(f"Folder found for folder_id: {folder_id}")
        else:
            logger.info(f"No folder found for folder_id: {folder_id}")
        return folder
    except Exception as e:
        logger.error(f"Failed to get folder by id: {e}")
        return None
    finally:
        db.close()


def get_all_folders() -> List[Folder]:
    """获取所有文件夹"""
    db = next(get_db())
    try:
        folders = (
            db.query(Folder)
            .order_by(Folder.created_at.asc())
            .all()
        )
        logger.info(f"Retrieved {len(folders)} folders")
        return folders
    except Exception as e:
        logger.error(f"Failed to get all folders: {e}")
        return []
    finally:
        db.close()


def delete_folder(folder_id: str) -> bool:
    """删除文件夹（递归删除子文件夹，但保留其中的历史记录，移动到根目录）"""
    db = next(get_db())
    try:
        # 首先检查文件夹是否存在
        folder = db.query(Folder).filter_by(id=folder_id).first()
        if not folder:
            logger.warning(f"Folder not found for folder_id: {folder_id}")
            return False
        
        # 递归获取所有子文件夹ID
        def get_subfolder_ids(parent_id: str) -> List[str]:
            subfolders = db.query(Folder).filter_by(parent_id=parent_id).all()
            subfolder_ids = [sf.id for sf in subfolders]
            for sf_id in subfolder_ids[:]:  # 创建副本以避免修改正在迭代的列表
                subfolder_ids.extend(get_subfolder_ids(sf_id))
            return subfolder_ids
        
        # 获取要删除的所有文件夹ID（包括自身和子文件夹）
        folder_ids_to_delete = [folder_id] + get_subfolder_ids(folder_id)
        
        # 将这些文件夹中的历史记录移动到根目录（设置folder_id为NULL）
        from app.db.models.history import History
        db.query(History).filter(History.folder_id.in_(folder_ids_to_delete)).update(
            {History.folder_id: None}, synchronize_session=False
        )
        
        # 删除所有相关文件夹
        db.query(Folder).filter(Folder.id.in_(folder_ids_to_delete)).delete(synchronize_session=False)
        
        db.commit()
        logger.info(f"Folder and subfolders deleted successfully. folder_ids: {folder_ids_to_delete}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete folder: {e}")
        return False
    finally:
        db.close()


def move_folder(folder_id: str, new_parent_id: Optional[str]) -> bool:
    """移动文件夹到新的父文件夹"""
    db = next(get_db())
    try:
        folder = db.query(Folder).filter_by(id=folder_id).first()
        if not folder:
            logger.warning(f"Folder not found for folder_id: {folder_id}")
            return False
        
        # 检查目标父文件夹是否存在（如果不是移动到根目录）
        if new_parent_id is not None:
            parent_folder = db.query(Folder).filter_by(id=new_parent_id).first()
            if not parent_folder:
                logger.warning(f"Parent folder not found for parent_id: {new_parent_id}")
                return False
        
        folder.parent_id = new_parent_id
        db.commit()
        logger.info(f"Folder moved successfully. folder_id: {folder_id}, new_parent_id: {new_parent_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to move folder: {e}")
        return False
    finally:
        db.close()