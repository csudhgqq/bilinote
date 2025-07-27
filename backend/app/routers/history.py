from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.db.history_dao import (
    get_all_history,
    get_history_by_task_id,
    delete_history,
    get_history_by_video,
    insert_history,
    update_history
)
from app.utils.response import ResponseWrapper as R
from app.services.note import NoteGenerator

router = APIRouter()


class HistoryResponse(BaseModel):
    id: int
    task_id: str
    status: str
    platform: str
    folder_id: Optional[str] = None
    title: Optional[str] = None
    cover_url: Optional[str] = None
    duration: Optional[int] = None
    file_path: Optional[str] = None
    video_id: Optional[str] = None
    raw_info: Optional[dict] = None
    transcript_full_text: Optional[str] = None
    transcript_language: Optional[str] = None
    transcript_raw: Optional[dict] = None
    transcript_segments: Optional[list] = None
    markdown_content: Optional[str] = None
    markdown_versions: Optional[list] = None
    form_data: Optional[dict] = None
    created_at: str
    updated_at: str


@router.get("/get_all_history")
def get_history_list(
    limit: int = Query(100, description="每页数量"),
    offset: int = Query(0, description="偏移量")
):
    """获取所有历史记录"""
    try:
        histories = get_all_history(limit=limit, offset=offset)
        result = []
        for history in histories:
            result.append({
                "id": history.id,
                "task_id": history.task_id,
                "status": history.status,
                "platform": history.platform,
                "folder_id": history.folder_id,
                "title": history.title,
                "cover_url": history.cover_url,
                "duration": history.duration,
                "file_path": history.file_path,
                "video_id": history.video_id,
                "raw_info": history.raw_info,
                "transcript_full_text": history.transcript_full_text,
                "transcript_language": history.transcript_language,
                "transcript_raw": history.transcript_raw,
                "transcript_segments": history.transcript_segments,
                "markdown_content": history.markdown_content,
                "markdown_versions": history.markdown_versions,
                "form_data": history.form_data,
                "created_at": history.created_at.isoformat() if history.created_at else None,
                "updated_at": history.updated_at.isoformat() if history.updated_at else None,
            })
        return R.success(data=result)
    except Exception as e:
        return R.error(msg=str(e))


class ImportHistoryRequest(BaseModel):
    task_id: str
    status: str
    platform: str
    title: Optional[str] = None
    cover_url: Optional[str] = None
    duration: Optional[float] = None  # 改为float类型，在适配器中转换为int
    file_path: Optional[str] = None
    video_id: Optional[str] = None
    raw_info: Optional[dict] = None
    transcript_full_text: Optional[str] = None
    transcript_language: Optional[str] = None
    transcript_raw: Optional[dict] = None
    transcript_segments: Optional[list] = None
    markdown_content: Optional[str] = None
    markdown_versions: Optional[list] = None
    form_data: Optional[dict] = None


@router.post("/import_history")
def import_single_history(data: ImportHistoryRequest):
    """导入单条历史记录"""
    try:
        # 先检查记录是否已存在
        existing_history = get_history_by_task_id(data.task_id)
        if existing_history:
            return R.error(msg=f"记录已存在: {data.task_id}")
        
        result = insert_history(
            task_id=data.task_id,
            status=data.status,
            platform=data.platform,
            title=data.title,
            cover_url=data.cover_url,
            duration=data.duration,
            file_path=data.file_path,
            video_id=data.video_id,
            raw_info=data.raw_info,
            transcript_full_text=data.transcript_full_text,
            transcript_language=data.transcript_language,
            transcript_raw=data.transcript_raw,
            transcript_segments=data.transcript_segments,
            markdown_content=data.markdown_content,
            markdown_versions=data.markdown_versions,
            form_data=data.form_data
        )
        
        if result:
            return R.success(msg="导入成功")
        else:
            return R.error(msg="导入失败")
    except Exception as e:
        return R.error(msg=str(e))


@router.post("/import_history_batch")
def import_batch_history(data: List[ImportHistoryRequest]):
    """批量导入历史记录，跳过已存在的记录"""
    try:
        success_count = 0
        error_count = 0
        skip_count = 0
        errors = []
        
        for item in data:
            try:
                # 先检查记录是否已存在
                existing_history = get_history_by_task_id(item.task_id)
                if existing_history:
                    skip_count += 1
                    continue
                
                result = insert_history(
                    task_id=item.task_id,
                    status=item.status,
                    platform=item.platform,
                    title=item.title,
                    cover_url=item.cover_url,
                    duration=item.duration,
                    file_path=item.file_path,
                    video_id=item.video_id,
                    raw_info=item.raw_info,
                    transcript_full_text=item.transcript_full_text,
                    transcript_language=item.transcript_language,
                    transcript_raw=item.transcript_raw,
                    transcript_segments=item.transcript_segments,
                    markdown_content=item.markdown_content,
                    markdown_versions=item.markdown_versions,
                    form_data=item.form_data
                )
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"导入失败: {item.task_id}")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"导入出错 {item.task_id}: {str(e)}")
        
        return R.success(
            data={
                "success_count": success_count,
                "skip_count": skip_count,
                "error_count": error_count,
                "errors": errors
            },
            msg=f"批量导入完成: 成功 {success_count} 条，跳过 {skip_count} 条，失败 {error_count} 条"
        )
    except Exception as e:
        return R.error(msg=str(e))


@router.get("/get_history/{task_id}")
def get_history_detail(task_id: str):
    """根据任务ID获取历史记录详情"""
    try:
        history = get_history_by_task_id(task_id)
        if not history:
            return R.error(msg="历史记录不存在")
        
        result = {
            "id": history.id,
            "task_id": history.task_id,
            "status": history.status,
            "platform": history.platform,
            "folder_id": history.folder_id,
            "title": history.title,
            "cover_url": history.cover_url,
            "duration": history.duration,
            "file_path": history.file_path,
            "video_id": history.video_id,
            "raw_info": history.raw_info,
            "transcript_full_text": history.transcript_full_text,
            "transcript_language": history.transcript_language,
            "transcript_raw": history.transcript_raw,
            "transcript_segments": history.transcript_segments,
            "markdown_content": history.markdown_content,
            "markdown_versions": history.markdown_versions,
            "form_data": history.form_data,
            "created_at": history.created_at.isoformat() if history.created_at else None,
            "updated_at": history.updated_at.isoformat() if history.updated_at else None,
        }
        return R.success(data=result)
    except Exception as e:
        return R.error(msg=str(e))


@router.delete("/delete_history/{task_id}")
def remove_history(task_id: str):
    """删除历史记录"""
    try:
        success = delete_history(task_id)
        if success:
            return R.success(msg="删除成功")
        else:
            return R.error(msg="删除失败，记录不存在")
    except Exception as e:
        return R.error(msg=str(e))


@router.get("/get_history_by_video")
def get_video_history(video_id: str, platform: str):
    """根据视频ID和平台获取历史记录"""
    try:
        histories = get_history_by_video(video_id, platform)
        result = []
        for history in histories:
            result.append({
                "id": history.id,
                "task_id": history.task_id,
                "status": history.status,
                "platform": history.platform,
                "title": history.title,
                "cover_url": history.cover_url,
                "duration": history.duration,
                "file_path": history.file_path,
                "video_id": history.video_id,
                "raw_info": history.raw_info,
                "transcript_full_text": history.transcript_full_text,
                "transcript_language": history.transcript_language,
                "transcript_raw": history.transcript_raw,
                "transcript_segments": history.transcript_segments,
                "markdown_content": history.markdown_content,
                "markdown_versions": history.markdown_versions,
                "form_data": history.form_data,
                "created_at": history.created_at.isoformat() if history.created_at else None,
                "updated_at": history.updated_at.isoformat() if history.updated_at else None,
            })
        return R.success(data=result)
    except Exception as e:
        return R.error(msg=str(e))


@router.put("/update_history/{task_id}")
def update_history_record(task_id: str, data: ImportHistoryRequest):
    """更新历史记录"""
    try:
        # 先检查记录是否存在
        existing_history = get_history_by_task_id(task_id)
        if not existing_history:
            return R.error(msg=f"记录不存在: {task_id}")
        
        # 准备数据字典并应用数据适配器
        data_dict = data.dict(exclude_unset=True)
        note_generator = NoteGenerator()
        adapted_data = note_generator._adapt_data_for_database(**data_dict)
        
        # 构建更新数据，只包含非None的字段
        update_data = {}
        for field, value in adapted_data.items():
            if field != 'task_id':  # task_id不允许更新
                update_data[field] = value
        
        # 更新记录
        result = update_history(task_id=task_id, **update_data)
        
        if result:
            return R.success(msg="更新成功")
        else:
            return R.error(msg="更新失败")
    except Exception as e:
        return R.error(msg=str(e))


@router.post("/upsert_history")
def upsert_history_record(data: ImportHistoryRequest):
    """插入或更新历史记录（存在则更新，不存在则插入）"""
    import traceback
    import json
    from app.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    try:
        # 记录接收到的原始数据
        logger.info(f"=== upsert_history API 调用开始 ===")
        logger.info(f"接收到的原始数据: {data.dict()}")
        
        # 先检查记录是否已存在
        existing_history = get_history_by_task_id(data.task_id)
        logger.info(f"检查现有记录结果: {'存在' if existing_history else '不存在'} (task_id: {data.task_id})")
        
        # 准备数据字典
        data_dict = data.dict(exclude_unset=True)
        logger.info(f"排除未设置字段后的数据: {json.dumps(data_dict, ensure_ascii=False, default=str)}")
        
        # 创建NoteGenerator实例并应用数据适配器
        logger.info("开始应用数据适配器...")
        note_generator = NoteGenerator()
        adapted_data = note_generator._adapt_data_for_database(**data_dict)
        logger.info(f"适配器处理后的数据: {json.dumps(adapted_data, ensure_ascii=False, default=str)}")
        
        if existing_history:
            # 记录存在，执行更新
            logger.info("执行更新操作...")
            update_data = {}
            for field, value in adapted_data.items():
                if field != 'task_id':  # task_id不允许更新
                    update_data[field] = value
            
            logger.info(f"更新数据字段: {list(update_data.keys())}")
            result = update_history(task_id=data.task_id, **update_data)
            
            if result:
                logger.info(f"记录更新成功 (task_id: {data.task_id})")
                return R.success(msg="更新成功")
            else:
                logger.error(f"记录更新失败 (task_id: {data.task_id})")
                return R.error(msg="更新失败")
        else:
            # 记录不存在，执行插入
            logger.info("执行插入操作...")
            insert_fields = {
                'task_id': adapted_data.get('task_id'),
                'status': adapted_data.get('status'),
                'platform': adapted_data.get('platform'),
                'title': adapted_data.get('title'),
                'cover_url': adapted_data.get('cover_url'),
                'duration': adapted_data.get('duration'),
                'file_path': adapted_data.get('file_path'),
                'video_id': adapted_data.get('video_id'),
                'raw_info': adapted_data.get('raw_info'),
                'transcript_full_text': adapted_data.get('transcript_full_text'),
                'transcript_language': adapted_data.get('transcript_language'),
                'transcript_raw': adapted_data.get('transcript_raw'),
                'transcript_segments': adapted_data.get('transcript_segments'),
                'markdown_content': adapted_data.get('markdown_content'),
                'markdown_versions': adapted_data.get('markdown_versions'),
                'form_data': adapted_data.get('form_data')
            }
            
            logger.info(f"插入数据字段摘要: task_id={insert_fields['task_id']}, status={insert_fields['status']}, platform={insert_fields['platform']}")
            
            result = insert_history(**insert_fields)
            
            if result:
                logger.info(f"记录插入成功 (task_id: {data.task_id})")
                return R.success(msg="创建成功")
            else:
                logger.error(f"记录插入失败 (task_id: {data.task_id})")
                return R.error(msg="创建失败")
                
    except Exception as e:
        # 详细的错误日志记录
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(f"=== upsert_history API 异常详情 ===")
        logger.error(f"任务ID: {getattr(data, 'task_id', 'UNKNOWN')}")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常消息: {error_msg}")
        logger.error(f"完整堆栈信息:\n{stack_trace}")
        logger.error(f"接收到的原始数据: {getattr(data, '__dict__', 'UNKNOWN')}")
        logger.error(f"=== 异常详情结束 ===")
        
        return R.error(msg=f"服务器内部错误: {error_msg}")
    finally:
        logger.info("=== upsert_history API 调用结束 ===\n") 