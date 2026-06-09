from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    operation_type: Optional[str] = None
    operation_module: Optional[str] = None
    operation_content: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    response_code: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    total: int
    items: List[AuditLogResponse]
