"""
数据管理相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DetectionDataCreate(BaseModel):
    task_id: int
    sample_id: int
    item_name: str
    item_code: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    standard_value: Optional[str] = None
    is_qualified: Optional[bool] = None
    test_method: Optional[str] = None
    equipment_id: Optional[int] = None
    equipment_name: Optional[str] = None
    environment: Optional[str] = None
    remarks: Optional[str] = None


class DetectionDataResponse(BaseModel):
    id: int
    task_id: int
    sample_id: int
    item_name: str
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    is_qualified: Optional[bool] = None
    tester_name: Optional[str] = None
    test_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class DetectionDataListResponse(BaseModel):
    total: int
    items: List[DetectionDataResponse]


class OriginalRecordCreate(BaseModel):
    task_id: int
    sample_id: int
    sample_no: str
    sample_name: str
    test_items: Optional[str] = None
    record_content: Optional[str] = None


class OriginalRecordResponse(BaseModel):
    id: int
    record_no: str
    task_id: int
    sample_no: str
    sample_name: str
    test_items: Optional[str] = None
    tester_name: Optional[str] = None
    test_date: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OriginalRecordListResponse(BaseModel):
    total: int
    items: List[OriginalRecordResponse]


class DataTraceCreate(BaseModel):
    sample_id: Optional[int] = None
    task_id: Optional[int] = None
    data_id: Optional[int] = None
    equipment_id: Optional[int] = None
    reagent_id: Optional[int] = None
    trace_type: str
    trace_content: Optional[str] = None


class DataTraceResponse(BaseModel):
    id: int
    trace_no: str
    trace_type: str
    trace_content: Optional[str] = None
    operator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataTraceListResponse(BaseModel):
    total: int
    items: List[DataTraceResponse]
