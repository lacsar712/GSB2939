"""
报告管理模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Report(Base):
    """报告表"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_no = Column(String(50), unique=True, nullable=False, comment="报告编号")
    task_id = Column(Integer, ForeignKey("tasks.id"), comment="任务ID")
    sample_id = Column(Integer, ForeignKey("samples.id"), comment="样品ID")
    sample_no = Column(String(50), comment="样品编号")
    sample_name = Column(String(200), comment="样品名称")
    customer_name = Column(String(100), comment="客户名称")
    test_items = Column(Text, comment="检测项目")
    test_results = Column(Text, comment="检测结果(JSON)")
    conclusion = Column(Text, comment="检测结论")
    status = Column(String(50), default="待审核", comment="状态(待审核/审核中/已签发/已退回)")
    template_id = Column(Integer, ForeignKey("report_templates.id"), comment="模板ID")
    prepared_by = Column(Integer, comment="编制人ID")
    prepared_by_name = Column(String(50), comment="编制人姓名")
    prepared_at = Column(DateTime, comment="编制时间")
    issued_by = Column(Integer, comment="签发人ID")
    issued_by_name = Column(String(50), comment="签发人姓名")
    issued_at = Column(DateTime, comment="签发时间")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    template = relationship("ReportTemplate", back_populates="reports")
    audits = relationship("ReportAudit", back_populates="report")


class ReportAudit(Base):
    """报告审核记录表"""
    __tablename__ = "report_audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, comment="报告ID")
    audit_level = Column(Integer, default=1, comment="审核级别(1/2/3)")
    auditor_id = Column(Integer, comment="审核人ID")
    auditor_name = Column(String(50), comment="审核人姓名")
    audit_result = Column(String(50), comment="审核结果(通过/退回)")
    audit_opinion = Column(Text, comment="审核意见")
    audited_at = Column(DateTime, default=datetime.now, comment="审核时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    report = relationship("Report", back_populates="audits")


class ReportTemplate(Base):
    """报告模板表"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_no = Column(String(50), unique=True, nullable=False, comment="模板编号")
    template_name = Column(String(200), nullable=False, comment="模板名称")
    template_type = Column(String(100), comment="模板类型")
    template_content = Column(Text, comment="模板内容")
    logo_url = Column(String(500), comment="Logo地址")
    header_content = Column(Text, comment="页眉内容")
    footer_content = Column(Text, comment="页脚内容")
    is_default = Column(Boolean, default=False, comment="是否默认")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    reports = relationship("Report", back_populates="template")
