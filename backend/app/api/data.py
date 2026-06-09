"""
数据管理 API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.data import DetectionData, OriginalRecord, DataTrace
from app.schemas.data import (
    DetectionDataCreate, DetectionDataResponse,
    OriginalRecordCreate, OriginalRecordResponse,
    DataTraceCreate, DataTraceResponse,
    DetectionDataListResponse, OriginalRecordListResponse, DataTraceListResponse
)
import logging

from app.core.deps import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


def generate_record_no(db: Session) -> str:
    """生成记录编号"""
    today = datetime.now().strftime("%Y%m%d")
    last_record = db.query(OriginalRecord).filter(
        OriginalRecord.record_no.like(f"OR{today}%")
    ).order_by(OriginalRecord.record_no.desc()).first()
    
    if last_record:
        try:
            last_seq = int(last_record.record_no[-4:])
            return f"OR{today}{str(last_seq + 1).zfill(4)}"
        except ValueError:
            pass
            
    return f"OR{today}0001"


# ==================== 检测数据管理 ====================

@router.get("/detection/", response_model=DetectionDataListResponse)
def get_detection_data(
    skip: int = 0,
    limit: int = 10,
    task_id: Optional[int] = None,
    sample_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取检测数据列表"""
    query = db.query(DetectionData)
    
    if task_id:
        query = query.filter(DetectionData.task_id == task_id)
    if sample_id:
        query = query.filter(DetectionData.sample_id == sample_id)
    
    total = query.count()
    data = query.order_by(DetectionData.created_at.desc()).offset(skip).limit(limit).all()
    items = [DetectionDataResponse.model_validate(item) for item in data]
    
    return {
        "total": total,
        "items": items
    }


@router.post("/detection/", response_model=DetectionDataResponse)
def create_detection_data(
    data_create: DetectionDataCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建检测数据"""
    data = DetectionData(
        **data_create.model_dump(),
        tester_name=current_user.username,
        test_date=datetime.now()
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    
    logger.info(f"Detection data created for task: {data_create.task_id} by {current_user.username}")
    return data


@router.put("/detection/{data_id}", response_model=DetectionDataResponse)
def update_detection_data(
    data_id: int, 
    result_value: float, 
    is_qualified: bool, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新检测数据"""
    data = db.query(DetectionData).filter(DetectionData.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="检测数据不存在")
    
    data.result_value = result_value
    data.is_qualified = is_qualified
    db.commit()
    db.refresh(data)
    return data


# ==================== 原始记录管理 ====================

@router.get("/records/", response_model=OriginalRecordListResponse)
def get_original_records(
    skip: int = 0,
    limit: int = 10,
    task_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取原始记录列表"""
    query = db.query(OriginalRecord)
    
    if task_id:
        query = query.filter(OriginalRecord.task_id == task_id)
    if status:
        query = query.filter(OriginalRecord.status == status)
    
    total = query.count()
    records = query.order_by(OriginalRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": records
    }


@router.get("/records/{record_id}", response_model=dict)
def get_original_record(
    record_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取原始记录详情"""
    record = db.query(OriginalRecord).filter(OriginalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="原始记录不存在")
    return record


@router.post("/records/", response_model=OriginalRecordResponse)
def create_original_record(
    record_create: OriginalRecordCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建原始记录"""
    record_no = generate_record_no(db)
    
    record = OriginalRecord(
        record_no=record_no,
        **record_create.model_dump(),
        tester_name=current_user.username,
        test_date=datetime.now(),
        status="待审核"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    logger.info(f"Original record created: {record.record_no} by {current_user.username}")
    return record


@router.put("/records/{record_id}/review")
def review_record(
    record_id: int, 
    approved: bool, 
    opinion: str = "", 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """审核原始记录"""
    record = db.query(OriginalRecord).filter(OriginalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="原始记录不存在")
    
    record.status = "已审核" if approved else "已退回"
    record.reviewer_name = current_user.username
    record.review_date = datetime.now()
    
    db.commit()
    
    return {"message": "审核完成"}


# ==================== 数据溯源 ====================

@router.get("/traces/", response_model=DataTraceListResponse)
def get_data_traces(
    skip: int = 0,
    limit: int = 10,
    sample_id: Optional[int] = None,
    task_id: Optional[int] = None,
    trace_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取数据溯源记录"""
    query = db.query(DataTrace)
    
    if sample_id:
        query = query.filter(DataTrace.sample_id == sample_id)
    if task_id:
        query = query.filter(DataTrace.task_id == task_id)
    if trace_type:
        query = query.filter(DataTrace.trace_type == trace_type)
    
    total = query.count()
    traces = query.order_by(DataTrace.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": traces
    }


@router.post("/traces/", response_model=DataTraceResponse)
def create_data_trace(
    trace_create: DataTraceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建数据溯源记录"""
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(DataTrace).filter(
        DataTrace.trace_no.like(f"TR{today}%")
    ).count()
    trace_no = f"TR{today}{str(count + 1).zfill(4)}"
    
    trace = DataTrace(
        trace_no=trace_no,
        **trace_create.model_dump(),
        operator_name=current_user.username
    )
    db.add(trace)
    db.commit()
    db.refresh(trace)
    return trace


@router.get("/traces/tree")
def get_trace_tree(
    sample_id: Optional[int] = None,
    task_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取溯源树形结构"""
    # 构建溯源树形结构
    tree = {
        "name": "溯源根节点",
        "children": []
    }
    
    if sample_id:
        # 样品溯源
        sample_traces = db.query(DataTrace).filter(
            DataTrace.sample_id == sample_id
        ).all()
        
        for trace in sample_traces:
            tree["children"].append({
                "name": trace.trace_no,
                "type": trace.trace_type,
                "content": trace.trace_content,
                "time": trace.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
    
    if task_id:
        # 任务溯源
        task_traces = db.query(DataTrace).filter(
            DataTrace.task_id == task_id
        ).all()
        
        for trace in task_traces:
            tree["children"].append({
                "name": trace.trace_no,
                "type": trace.trace_type,
                "content": trace.trace_content,
                "time": trace.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return tree
