"""
样品管理 API
"""
from typing import List, Optional
from datetime import datetime
from io import BytesIO
import openpyxl
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.sample import Sample, SampleStorage, SampleTransfer
from app.models.task import Task
from app.schemas.task import TaskResponse
from app.models.audit import AuditLog
from app.schemas.sample import (
    SampleCreate, SampleUpdate, SampleResponse, SampleListResponse, SampleDetailResponse,
    SampleStorageCreate, SampleStorageUpdate, SampleStorageResponse,
    SampleTransferCreate, SampleTransferResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def generate_sample_no(db: Session) -> str:
    """生成样品编号"""
    today = datetime.now().strftime("%Y%m%d")
    last_sample = db.query(Sample).filter(
        Sample.sample_no.like(f"SP{today}%")
    ).order_by(Sample.sample_no.desc()).first()
    
    if last_sample:
        try:
            last_seq = int(last_sample.sample_no[-4:])
            return f"SP{today}{str(last_seq + 1).zfill(4)}"
        except ValueError:
            # Fallback if parsing fails
            pass
            
    return f"SP{today}0001"


@router.post("/import", response_model=dict)
def import_samples(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入样品 (Excel)"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件 (.xlsx, .xls)")
    
    try:
        contents = file.file.read()
        wb = openpyxl.load_workbook(BytesIO(contents))
        ws = wb.active
        
        # Get headers
        headers = [cell.value for cell in ws[1]]
        header_map = {
            "样品名称": "name",
            "样品类型": "type",
            "来源": "source",
            "批号": "batch_no",
            "数量": "quantity",
            "单位": "unit",
            "客户名称": "customer_name",
            "联系人": "customer_contact",
            "联系电话": "customer_phone",
            "备注": "remarks"
        }
        
        # Build index map
        col_indices = {h: i for i, h in enumerate(headers) if h in header_map}
        
        imported_count = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            # Check required name
            name_idx = col_indices.get("样品名称")
            if name_idx is None or not row[name_idx]:
                continue
                
            data = {}
            for header, field in header_map.items():
                if header in col_indices:
                    val = row[col_indices[header]]
                    if val is not None:
                        data[field] = val
            
            # Create sample
            sample_no = generate_sample_no(db)
            
            sample = Sample(
                sample_no=sample_no,
                name=data.get('name'),
                type=data.get('type', '常规'),
                source=data.get('source', '送检'),
                batch_no=str(data.get('batch_no')) if data.get('batch_no') else None,
                quantity=float(data.get('quantity', 1.0)),
                unit=data.get('unit', '个'),
                customer_name=data.get('customer_name', '未知'),
                customer_contact=str(data.get('customer_contact')) if data.get('customer_contact') else None,
                customer_phone=str(data.get('customer_phone')) if data.get('customer_phone') else None,
                remarks=str(data.get('remarks')) if data.get('remarks') else None,
                receive_date=datetime.now(),
                status="已登记",
                created_by=current_user.id
            )
            
            db.add(sample)
            db.flush()
            
            # Transfer log
            transfer = SampleTransfer(
                sample_id=sample.id,
                to_status="已登记",
                operation="批量导入",
                operator_id=current_user.id,
                operator_name=current_user.real_name
            )
            db.add(transfer)
            imported_count += 1
            
        db.commit()
        return {"message": "导入成功", "count": imported_count}
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/", response_model=SampleListResponse)
def get_samples(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    storage_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取样品列表"""
    query = db.query(Sample)
    
    if status:
        query = query.filter(Sample.status == status)
    if storage_id is not None:
        query = query.filter(Sample.storage_id == storage_id)
    if keyword:
        query = query.filter(
            (Sample.sample_no.contains(keyword)) |
            (Sample.name.contains(keyword)) |
            (Sample.customer_name.contains(keyword))
        )
    
    total = query.count()
    samples = query.order_by(Sample.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [SampleResponse.model_validate(s) for s in samples]
    }


@router.get("/{sample_id}", response_model=SampleDetailResponse)
def get_sample(
    sample_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取样品详情"""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="样品不存在")
    
    # 获取流转记录
    transfers = db.query(SampleTransfer).filter(
        SampleTransfer.sample_id == sample_id
    ).order_by(SampleTransfer.created_at.desc()).all()
    
    tasks = db.query(Task).filter(Task.sample_id == sample_id).all()
    return SampleDetailResponse(
        sample=SampleResponse.model_validate(sample),
        transfers=[SampleTransferResponse.model_validate(t) for t in transfers],
        tasks=[TaskResponse.model_validate(t) for t in tasks]
    )


@router.post("/", response_model=SampleResponse)
def create_sample(
    sample_create: SampleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建样品"""
    sample_no = generate_sample_no(db)
    
    sample = Sample(
        sample_no=sample_no,
        name=sample_create.name,
        source=sample_create.source,
        type=sample_create.type,
        batch_no=sample_create.batch_no,
        quantity=sample_create.quantity,
        unit=sample_create.unit,
        customer_name=sample_create.customer_name,
        customer_contact=sample_create.customer_contact,
        customer_phone=sample_create.customer_phone,
        expected_date=sample_create.expected_date,
        remarks=sample_create.remarks,
        receive_date=datetime.now(),
        status="已登记",
        created_by=current_user.id
    )
    
    db.add(sample)
    db.flush()
    
    # 添加流转记录
    transfer = SampleTransfer(
        sample_id=sample.id,
        to_status="已登记",
        operation="样品登记",
        operator_id=current_user.id,
        operator_name=current_user.real_name
    )
    db.add(transfer)
    
    db.commit()
    db.refresh(sample)
    
    logger.info(f"Sample created: {sample.sample_no}")
    return sample


@router.put("/{sample_id}", response_model=SampleResponse)
def update_sample(
    sample_id: int, 
    sample_update: SampleUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新样品"""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="样品不存在")
    
    update_data = sample_update.model_dump(exclude_unset=True)
    
    # 记录状态变更
    if 'status' in update_data and update_data['status'] != sample.status:
        transfer = SampleTransfer(
            sample_id=sample_id,
            from_status=sample.status,
            to_status=update_data['status'],
            operation="状态变更",
            operator_id=current_user.id,
            operator_name=current_user.real_name
        )
        db.add(transfer)
    
    for field, value in update_data.items():
        setattr(sample, field, value)
    
    db.commit()
    db.refresh(sample)
    
    logger.info(f"Sample updated: {sample.sample_no}")
    return sample


@router.delete("/{sample_id}")
def delete_sample(
    sample_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除样品"""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="样品不存在")
    
    db.delete(sample)
    db.commit()
    
    logger.info(f"Sample deleted: {sample.sample_no}")
    return {"message": "删除成功"}


# ==================== 存储位置管理 ====================

@router.get("/storages/", response_model=List[SampleStorageResponse])
def get_storages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取存储位置列表"""
    storages = db.query(SampleStorage).all()
    return [SampleStorageResponse.model_validate(s) for s in storages]


@router.post("/storages/", response_model=SampleStorageResponse)
def create_storage(
    storage_create: SampleStorageCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建存储位置"""
    storage = SampleStorage(**storage_create.model_dump())
    db.add(storage)
    db.commit()
    db.refresh(storage)
    return storage


@router.put("/storages/{storage_id}", response_model=SampleStorageResponse)
def update_storage(
    storage_id: int,
    storage_update: SampleStorageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新存储位置"""
    storage = db.query(SampleStorage).filter(SampleStorage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="存储位置不存在")
    
    update_data = storage_update.model_dump(exclude_unset=True)
    
    # Check parent loop
    if 'parent_id' in update_data and update_data['parent_id'] is not None:
        parent_id = update_data['parent_id']
        if parent_id == storage_id:
            raise HTTPException(status_code=400, detail="不能将自己设为父节点")
        
        # Check if parent is a child of current node
        parent = db.query(SampleStorage).filter(SampleStorage.id == parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父节点不存在")
            
        current = parent
        while current.parent_id:
            if current.parent_id == storage_id:
                raise HTTPException(status_code=400, detail="不能将节点移动到其子节点下")
            current = db.query(SampleStorage).filter(SampleStorage.id == current.parent_id).first()
            if not current:
                break
    
    for field, value in update_data.items():
        setattr(storage, field, value)
    
    db.commit()
    db.refresh(storage)
    return storage


@router.delete("/storages/{storage_id}")
def delete_storage(
    storage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除存储位置"""
    storage = db.query(SampleStorage).filter(SampleStorage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="存储位置不存在")
        
    # Check if has children
    children = db.query(SampleStorage).filter(SampleStorage.parent_id == storage_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="存在子节点，无法删除")
        
    # Check if has samples
    samples = db.query(Sample).filter(Sample.storage_id == storage_id).count()
    if samples > 0:
        raise HTTPException(status_code=400, detail="该位置有样品，无法删除")
        
    db.delete(storage)
    db.commit()
    return {"message": "删除成功"}


# ==================== 流转记录 ====================

@router.get("/{sample_id}/transfers/", response_model=List[SampleTransferResponse])
def get_sample_transfers(
    sample_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取样品流转记录"""
    transfers = db.query(SampleTransfer).filter(
        SampleTransfer.sample_id == sample_id
    ).order_by(SampleTransfer.created_at.desc()).all()
    return [SampleTransferResponse.model_validate(t) for t in transfers]


@router.post("/transfers/", response_model=SampleTransferResponse)
def create_transfer(
    transfer_create: SampleTransferCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建流转记录"""
    transfer = SampleTransfer(
        **transfer_create.model_dump(), 
        operator_id=current_user.id,
        operator_name=current_user.real_name
    )
    db.add(transfer)
    
    # 更新样品状态
    if transfer_create.to_status:
        sample = db.query(Sample).filter(Sample.id == transfer_create.sample_id).first()
        if sample:
            sample.status = transfer_create.to_status
    
    db.commit()
    db.refresh(transfer)
    return transfer
