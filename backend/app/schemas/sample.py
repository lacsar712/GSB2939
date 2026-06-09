"""
样品相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.task import TaskResponse


class SampleCreate(BaseModel):
    name: str
    source: Optional[str] = None
    type: Optional[str] = None
    batch_no: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    expected_date: Optional[datetime] = None
    remarks: Optional[str] = None


class SampleUpdate(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    type: Optional[str] = None
    batch_no: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    expected_date: Optional[datetime] = None
    remarks: Optional[str] = None
    storage_id: Optional[int] = None


class SampleResponse(BaseModel):
    id: int
    sample_no: str
    name: str
    source: Optional[str] = None
    type: Optional[str] = None
    batch_no: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: str
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    receive_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    remarks: Optional[str] = None
    storage_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SampleListResponse(BaseModel):
    total: int
    items: List[SampleResponse]


class SampleStorageCreate(BaseModel):
    location_code: str
    location_name: str
    location_type: Optional[str] = None
    parent_id: Optional[int] = None
    capacity: Optional[int] = 100
    temperature: Optional[str] = None
    humidity: Optional[str] = None


class SampleStorageUpdate(BaseModel):
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    location_type: Optional[str] = None
    parent_id: Optional[int] = None
    capacity: Optional[int] = None
    temperature: Optional[str] = None
    humidity: Optional[str] = None
    status: Optional[str] = None


class SampleStorageResponse(BaseModel):
    id: int
    location_code: str
    location_name: str
    location_type: Optional[str] = None
    parent_id: Optional[int] = None
    capacity: int
    used_capacity: int
    temperature: Optional[str] = None
    humidity: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class SampleTransferCreate(BaseModel):
    sample_id: int
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    operation: str
    remarks: Optional[str] = None


class SampleTransferResponse(BaseModel):
    id: int
    sample_id: int
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    operator_name: Optional[str] = None
    operation: str
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SampleDetailResponse(BaseModel):
    sample: SampleResponse
    transfers: List[SampleTransferResponse]
    tasks: List[TaskResponse]

    class Config:
        from_attributes = True
