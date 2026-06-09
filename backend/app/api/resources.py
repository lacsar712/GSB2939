"""
资源管理 API (试剂/设备/耗材)
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.resource import Reagent, Equipment, Consumable, ConsumableRecord
from app.schemas.resource import (
    ReagentCreate, ReagentResponse, ReagentList,
    EquipmentCreate, EquipmentResponse, EquipmentList,
    ConsumableCreate, ConsumableResponse, ConsumableList
)
import logging

from app.core.deps import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== 试剂管理 ====================

@router.get("/reagents/", response_model=ReagentList)
def get_reagents(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    show_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取试剂列表"""
    query = db.query(Reagent)
    
    if category:
        query = query.filter(Reagent.category == category)
    if keyword:
        query = query.filter(
            (Reagent.reagent_no.contains(keyword)) |
            (Reagent.name.contains(keyword))
        )
    if not show_expired:
        query = query.filter(Reagent.is_expired == False)
    
    total = query.count()
    reagents = query.order_by(Reagent.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": reagents
    }


@router.post("/reagents/", response_model=ReagentResponse)
def create_reagent(
    reagent_create: ReagentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建试剂"""
    today = datetime.now().strftime("%Y%m%d")
    last_item = db.query(Reagent).filter(
        Reagent.reagent_no.like(f"RG{today}%")
    ).order_by(Reagent.reagent_no.desc()).first()
    
    seq = 1
    if last_item:
        try:
            seq = int(last_item.reagent_no[-4:]) + 1
        except ValueError:
            pass
    reagent_no = f"RG{today}{str(seq).zfill(4)}"
    
    # 检查是否过期
    is_expired = False
    if reagent_create.expiry_date:
        is_expired = reagent_create.expiry_date < date.today()
    
    reagent = Reagent(
        reagent_no=reagent_no,
        **reagent_create.model_dump(),
        is_expired=is_expired
    )
    db.add(reagent)
    db.commit()
    db.refresh(reagent)
    
    logger.info(f"Reagent created: {reagent.reagent_no} by {current_user.username}")
    return reagent


@router.put("/reagents/{reagent_id}", response_model=ReagentResponse)
def update_reagent(
    reagent_id: int, 
    quantity: float, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新试剂库存"""
    reagent = db.query(Reagent).filter(Reagent.id == reagent_id).first()
    if not reagent:
        raise HTTPException(status_code=404, detail="试剂不存在")
    
    reagent.quantity = quantity
    db.commit()
    db.refresh(reagent)
    return reagent


@router.get("/reagents/warning")
def get_reagent_warnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取试剂预警列表"""
    # 库存预警
    low_stock = db.query(Reagent).filter(
        Reagent.quantity <= Reagent.warning_quantity
    ).all()
    
    # 过期预警
    expired = db.query(Reagent).filter(
        Reagent.is_expired == True
    ).all()
    
    # 即将过期（30天内）
    from datetime import timedelta
    soon_expired = db.query(Reagent).filter(
        Reagent.expiry_date <= date.today() + timedelta(days=30),
        Reagent.expiry_date > date.today()
    ).all()
    
    return {
        "low_stock": low_stock,
        "expired": expired,
        "soon_expired": soon_expired
    }


# ==================== 设备管理 ====================

@router.get("/equipments/", response_model=EquipmentList)
def get_equipments(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备列表"""
    query = db.query(Equipment)
    
    if category:
        query = query.filter(Equipment.category == category)
    if status:
        query = query.filter(Equipment.status == status)
    if keyword:
        query = query.filter(
            (Equipment.equipment_no.contains(keyword)) |
            (Equipment.name.contains(keyword))
        )
    
    total = query.count()
    equipments = query.order_by(Equipment.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": equipments
    }


@router.post("/equipments/", response_model=EquipmentResponse)
def create_equipment(
    equipment_create: EquipmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建设备"""
    today = datetime.now().strftime("%Y%m%d")
    last_item = db.query(Equipment).filter(
        Equipment.equipment_no.like(f"EQ{today}%")
    ).order_by(Equipment.equipment_no.desc()).first()
    
    seq = 1
    if last_item:
        try:
            seq = int(last_item.equipment_no[-4:]) + 1
        except ValueError:
            pass
    equipment_no = f"EQ{today}{str(seq).zfill(4)}"
    
    equipment = Equipment(
        equipment_no=equipment_no,
        **equipment_create.model_dump()
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    
    logger.info(f"Equipment created: {equipment.equipment_no} by {current_user.username}")
    return equipment


@router.put("/equipments/{equipment_id}/calibration")
def update_calibration(
    equipment_id: int,
    calibration_date: date,
    next_date: date,
    organization: str,
    result: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新设备校准信息"""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    equipment.last_calibration_date = calibration_date
    equipment.next_calibration_date = next_date
    equipment.calibration_organization = organization
    equipment.calibration_result = result
    
    db.commit()
    
    return {"message": "校准信息更新成功"}


@router.get("/equipments/calibration-warning")
def get_calibration_warnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取校准预警列表"""
    from datetime import timedelta
    
    # 即将到期（30天内）
    soon_due = db.query(Equipment).filter(
        Equipment.next_calibration_date <= date.today() + timedelta(days=30),
        Equipment.next_calibration_date > date.today(),
        Equipment.status == "正常"
    ).all()
    
    # 已过期
    overdue = db.query(Equipment).filter(
        Equipment.next_calibration_date < date.today(),
        Equipment.status == "正常"
    ).all()
    
    return {
        "soon_due": soon_due,
        "overdue": overdue
    }


# ==================== 耗材管理 ====================

@router.get("/consumables/", response_model=ConsumableList)
def get_consumables(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取耗材列表"""
    query = db.query(Consumable)
    
    if category:
        query = query.filter(Consumable.category == category)
    if keyword:
        query = query.filter(
            (Consumable.consumable_no.contains(keyword)) |
            (Consumable.name.contains(keyword))
        )
    
    total = query.count()
    consumables = query.order_by(Consumable.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": consumables
    }


@router.post("/consumables/", response_model=ConsumableResponse)
def create_consumable(
    consumable_create: ConsumableCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建耗材"""
    today = datetime.now().strftime("%Y%m%d")
    last_item = db.query(Consumable).filter(
        Consumable.consumable_no.like(f"CS{today}%")
    ).order_by(Consumable.consumable_no.desc()).first()
    
    seq = 1
    if last_item:
        try:
            seq = int(last_item.consumable_no[-4:]) + 1
        except ValueError:
            pass
    consumable_no = f"CS{today}{str(seq).zfill(4)}"
    
    consumable = Consumable(
        consumable_no=consumable_no,
        **consumable_create.model_dump()
    )
    db.add(consumable)
    db.commit()
    db.refresh(consumable)
    
    logger.info(f"Consumable created: {consumable.consumable_no} by {current_user.username}")
    return consumable


@router.post("/consumables/{consumable_id}/operation")
def consumable_operation(
    consumable_id: int,
    operation_type: str,
    quantity: float,
    department: str = "",
    remarks: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """耗材出入库操作"""
    consumable = db.query(Consumable).filter(Consumable.id == consumable_id).first()
    if not consumable:
        raise HTTPException(status_code=404, detail="耗材不存在")
    
    if operation_type == "领用" and consumable.quantity < quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    
    # 更新库存
    if operation_type == "入库":
        consumable.quantity += quantity
    elif operation_type == "领用":
        consumable.quantity -= quantity
    
    # 记录操作
    record = ConsumableRecord(
        consumable_id=consumable_id,
        consumable_name=consumable.name,
        record_type=operation_type,
        quantity=quantity,
        unit=consumable.unit,
        operator_name=current_user.username,
        department=department,
        remarks=remarks
    )
    
    db.add(record)
    db.commit()
    
    return {"message": "操作成功", "current_quantity": consumable.quantity}


@router.get("/consumables/warning")
def get_consumable_warnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取耗材库存预警"""
    low_stock = db.query(Consumable).filter(
        Consumable.quantity <= Consumable.warning_quantity
    ).all()
    
    return {
        "low_stock": low_stock
    }
