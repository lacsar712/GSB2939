"""
审计追踪 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse, AuditLogListResponse
import logging

from app.core.deps import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/logs/", response_model=AuditLogListResponse)
def get_audit_logs(
    skip: int = 0,
    limit: int = 10,
    user_name: Optional[str] = None,
    operation_type: Optional[str] = None,
    operation_module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取审计日志列表"""
    query = db.query(AuditLog)
    
    if user_name:
        query = query.filter(AuditLog.user_name.contains(user_name))
    if operation_type:
        query = query.filter(AuditLog.operation_type == operation_type)
    if operation_module:
        query = query.filter(AuditLog.operation_module == operation_module)
    if start_date:
        from datetime import datetime
        query = query.filter(AuditLog.created_at >= datetime.parse(start_date))
    if end_date:
        from datetime import datetime
        from datetime import timedelta
        query = query.filter(AuditLog.created_at <= datetime.parse(end_date) + timedelta(days=1))
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": logs
    }


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取审计日志详情"""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log


@router.post("/logs/")
def create_audit_log(
    user_id: int,
    user_name: str,
    operation_type: str,
    operation_module: str,
    operation_content: str,
    request_url: str = "",
    request_method: str = "",
    ip_address: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建审计日志"""
    log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        operation_type=operation_type,
        operation_module=operation_module,
        operation_content=operation_content,
        request_url=request_url,
        request_method=request_method,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()
    
    return {"message": "日志创建成功"}


@router.get("/operation-types/")
def get_operation_types(current_user: User = Depends(get_current_active_user)):
    """获取操作类型列表"""
    return {
        "items": [
            {"value": "登录", "label": "登录"},
            {"value": "登出", "label": "登出"},
            {"value": "新增", "label": "新增"},
            {"value": "修改", "label": "修改"},
            {"value": "删除", "label": "删除"},
            {"value": "导出", "label": "导出"},
            {"value": "打印", "label": "打印"},
            {"value": "审核", "label": "审核"},
            {"value": "签发", "label": "签发"}
        ]
    }


@router.get("/modules/")
def get_operation_modules(current_user: User = Depends(get_current_active_user)):
    """获取操作模块列表"""
    return {
        "items": [
            {"value": "用户管理", "label": "用户管理"},
            {"value": "样品管理", "label": "样品管理"},
            {"value": "任务管理", "label": "任务管理"},
            {"value": "数据管理", "label": "数据管理"},
            {"value": "试剂管理", "label": "试剂管理"},
            {"value": "设备管理", "label": "设备管理"},
            {"value": "耗材管理", "label": "耗材管理"},
            {"value": "报告管理", "label": "报告管理"},
            {"value": "系统设置", "label": "系统设置"}
        ]
    }
