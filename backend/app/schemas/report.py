"""
报告相关 Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportCreate(BaseModel):
    task_id: int
    sample_id: int
    sample_no: str
    sample_name: str
    customer_name: Optional[str] = None
    test_items: Optional[str] = None
    test_results: Optional[str] = None
    conclusion: Optional[str] = None
    template_id: Optional[int] = None
    remarks: Optional[str] = None


class ReportUpdate(BaseModel):
    test_results: Optional[str] = None
    conclusion: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    report_no: str
    task_id: int
    sample_no: str
    sample_name: str
    customer_name: Optional[str] = None
    test_items: Optional[str] = None
    conclusion: Optional[str] = None
    status: str
    prepared_by_name: Optional[str] = None
    prepared_at: Optional[datetime] = None
    issued_by_name: Optional[str] = None
    issued_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportList(BaseModel):
    total: int
    items: list[ReportResponse]


class ReportAuditCreate(BaseModel):
    report_id: int
    audit_level: int
    audit_result: str
    audit_opinion: Optional[str] = None


class ReportAuditResponse(BaseModel):
    id: int
    report_id: int
    audit_level: int
    auditor_name: str
    audit_result: str
    audit_opinion: Optional[str] = None
    audited_at: datetime

    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    report: ReportResponse
    audits: list[ReportAuditResponse]


class ReportTemplateCreate(BaseModel):
    template_no: str
    template_name: str
    template_type: Optional[str] = None
    template_content: Optional[str] = None
    logo_url: Optional[str] = None
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    is_default: Optional[bool] = False


class ReportTemplateUpdate(BaseModel):
    template_no: Optional[str] = None
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    template_content: Optional[str] = None
    logo_url: Optional[str] = None
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(BaseModel):
    id: int
    template_no: str
    template_name: str
    template_type: Optional[str] = None
    template_content: Optional[str] = None
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportTemplateList(BaseModel):
    total: int
    items: list[ReportTemplateResponse]

