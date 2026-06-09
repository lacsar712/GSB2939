"""
任务相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TaskCreate(BaseModel):
    sample_id: int
    sample_no: str
    sample_name: str
    test_items: Optional[str] = None
    standard_method_id: Optional[int] = None
    priority: Optional[str] = "普通"
    deadline: Optional[datetime] = None
    department: Optional[str] = None
    remarks: Optional[str] = None


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    department: Optional[str] = None
    progress: Optional[int] = None
    remarks: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    task_no: str
    sample_id: int
    sample_no: str
    sample_name: str
    test_items: Optional[str] = None
    standard_method_id: Optional[int] = None
    status: str
    priority: str
    deadline: Optional[datetime] = None
    department: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    progress: int
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskAssignmentResponse(BaseModel):
    id: int
    task_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    assigned_by: Optional[int] = None
    assigned_by_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskDetailResponse(BaseModel):
    task: TaskResponse
    assignments: List[TaskAssignmentResponse]

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    total: int
    items: List[TaskResponse]

    class Config:
        from_attributes = True


class StandardMethodCreate(BaseModel):
    method_no: str
    method_name: str
    standard_type: Optional[str] = None
    standard_no: Optional[str] = None
    version: Optional[str] = None
    test_items: Optional[str] = None
    equipment_required: Optional[str] = None
    reagent_required: Optional[str] = None
    description: Optional[str] = None


class StandardMethodResponse(BaseModel):
    id: int
    method_no: str
    method_name: str
    standard_type: Optional[str] = None
    standard_no: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class StandardMethodListResponse(BaseModel):
    total: int
    items: List[StandardMethodResponse]

    class Config:
        from_attributes = True


class TaskAssignmentCreate(BaseModel):
    task_id: int
    user_id: int
    user_name: str
    department: Optional[str] = None
    remarks: Optional[str] = None


class TaskAssignmentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    user_name: str
    department: Optional[str] = None
    status: str
    assigned_at: datetime

    class Config:
        from_attributes = True
