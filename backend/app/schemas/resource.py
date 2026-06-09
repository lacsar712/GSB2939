"""
试剂设备相关 Schema
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class ReagentCreate(BaseModel):
    name: str
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_no: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = 0
    unit: Optional[str] = None
    warning_quantity: Optional[float] = 10
    location: Optional[str] = None
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None
    price: Optional[float] = None
    remarks: Optional[str] = None


class ReagentResponse(BaseModel):
    id: int
    reagent_no: str
    name: str
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_no: Optional[str] = None
    category: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    warning_quantity: float
    location: Optional[str] = None
    expiry_date: Optional[date] = None
    is_expired: bool
    supplier: Optional[str] = None

    class Config:
        from_attributes = True


class ReagentList(BaseModel):
    total: int
    items: list[ReagentResponse]


class EquipmentCreate(BaseModel):
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_no: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    warranty_date: Optional[date] = None
    last_calibration_date: Optional[date] = None
    next_calibration_date: Optional[date] = None
    calibration_organization: Optional[str] = None
    responsible_person: Optional[str] = None
    remarks: Optional[str] = None


class EquipmentResponse(BaseModel):
    id: int
    equipment_no: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_no: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    status: str
    next_calibration_date: Optional[date] = None
    responsible_person: Optional[str] = None

    class Config:
        from_attributes = True


class ConsumableCreate(BaseModel):
    name: str
    specification: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = 0
    unit: Optional[str] = None
    warning_quantity: Optional[float] = 10
    location: Optional[str] = None
    supplier: Optional[str] = None
    price: Optional[float] = None
    remarks: Optional[str] = None


class ConsumableResponse(BaseModel):
    id: int
    consumable_no: str
    name: str
    specification: Optional[str] = None
    category: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    warning_quantity: float
    location: Optional[str] = None
    supplier: Optional[str] = None

    class Config:
        from_attributes = True


class EquipmentList(BaseModel):
    total: int
    items: list[EquipmentResponse]


class ConsumableList(BaseModel):
    total: int
    items: list[ConsumableResponse]
