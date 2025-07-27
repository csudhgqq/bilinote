from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.db import folder_dao, history_dao
from app.utils.logger import get_logger
from app.utils.response import ResponseWrapper as R

logger = get_logger(__name__)
router = APIRouter()


class FolderCreateRequest(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    is_expanded: bool = True


class FolderUpdateRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[str] = None
    is_expanded: Optional[bool] = None


class MoveHistoryRequest(BaseModel):
    task_id: str
    folder_id: Optional[str] = None


class FolderResponse(BaseModel):
    id: str
    name: str
    parent_id: Optional[str]
    is_expanded: bool
    created_at: str
    updated_at: str


@router.post("/folders")
async def create_folder(request: FolderCreateRequest):
    """创建新文件夹"""
    try:
        folder = folder_dao.insert_folder(
            folder_id=request.id,
            name=request.name,
            parent_id=request.parent_id,
            is_expanded=request.is_expanded
        )
        
        if not folder:
            return R.error("Failed to create folder", 400)
        
        folder_data = FolderResponse(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            is_expanded=folder.is_expanded,
            created_at=folder.created_at.isoformat(),
            updated_at=folder.updated_at.isoformat()
        )
        return R.success(folder_data.dict(), "Folder created successfully")
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return R.error("Internal server error", 500)


@router.get("/folders")
async def get_all_folders():
    """获取所有文件夹"""
    try:
        folders = folder_dao.get_all_folders()
        folder_list = [
            FolderResponse(
                id=folder.id,
                name=folder.name,
                parent_id=folder.parent_id,
                is_expanded=folder.is_expanded,
                created_at=folder.created_at.isoformat(),
                updated_at=folder.updated_at.isoformat()
            ).dict()
            for folder in folders
        ]
        return R.success(folder_list, "Folders retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        return R.error("Internal server error", 500)


@router.put("/folders/{folder_id}")
async def update_folder(folder_id: str, request: FolderUpdateRequest):
    """更新文件夹"""
    try:
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.parent_id is not None:
            update_data['parent_id'] = request.parent_id
        if request.is_expanded is not None:
            update_data['is_expanded'] = request.is_expanded
        
        folder = folder_dao.update_folder(folder_id, **update_data)
        if not folder:
            return R.error("Folder not found", 404)
        
        folder_data = FolderResponse(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            is_expanded=folder.is_expanded,
            created_at=folder.created_at.isoformat(),
            updated_at=folder.updated_at.isoformat()
        )
        return R.success(folder_data.dict(), "Folder updated successfully")
    except Exception as e:
        logger.error(f"Error updating folder: {e}")
        return R.error("Internal server error", 500)


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str):
    """删除文件夹"""
    try:
        success = folder_dao.delete_folder(folder_id)
        if not success:
            return R.error("Folder not found", 404)
        
        return R.success(None, "Folder deleted successfully")
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        return R.error("Internal server error", 500)


@router.post("/folders/move-history")
async def move_history_to_folder(request: MoveHistoryRequest):
    """将历史记录移动到文件夹"""
    try:
        success = history_dao.move_history_to_folder(request.task_id, request.folder_id)
        if not success:
            return R.error("History record or folder not found", 404)
        
        return R.success(None, "History moved successfully")
    except Exception as e:
        logger.error(f"Error moving history: {e}")
        return R.error("Internal server error", 500)