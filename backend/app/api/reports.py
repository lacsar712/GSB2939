"""
报告管理 API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.report import Report, ReportAudit, ReportTemplate
from app.models.data import DetectionData
from app.models.task import Task
from app.models.sample import Sample
from app.schemas.report import (
    ReportCreate, ReportUpdate, ReportResponse, ReportList, ReportDetail,
    ReportAuditCreate, ReportAuditResponse,
    ReportTemplateCreate, ReportTemplateResponse, ReportTemplateUpdate,
    ReportTemplateList
)
import logging
import json
from pydantic import BaseModel

from app.core.deps import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


def generate_report_no(db: Session) -> str:
    """生成报告编号"""
    today = datetime.now().strftime("%Y%m%d")
    last_report = db.query(Report).filter(
        Report.report_no.like(f"RP{today}%")
    ).order_by(Report.report_no.desc()).first()
    
    if last_report:
        try:
            last_seq = int(last_report.report_no[-4:])
            return f"RP{today}{str(last_seq + 1).zfill(4)}"
        except ValueError:
            pass
            
    return f"RP{today}0001"


class ReportGenerateRequest(BaseModel):
    task_id: int
    template_id: int


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从任务生成报告"""
    # 1. Check if task exists
    task = db.query(Task).filter(Task.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 2. Check if template exists
    template = db.query(ReportTemplate).filter(ReportTemplate.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="报告模板不存在")
        
    # 3. Get Sample info
    sample = db.query(Sample).filter(Sample.id == task.sample_id).first()
    
    # 4. Get Detection Data
    results = db.query(DetectionData).filter(DetectionData.task_id == request.task_id).all()
    
    # 5. Serialize Results
    results_list = [
        {
            "item_name": r.item_name,
            "result_value": r.result_value,
            "result_unit": r.result_unit,
            "standard_value": r.standard_value,
            "is_qualified": r.is_qualified
        }
        for r in results
    ]
    
    # 6. Determine Conclusion
    all_qualified = all(r.is_qualified for r in results) if results else False
    conclusion = "该样品所检项目符合标准要求。" if all_qualified else "该样品所检项目不符合标准要求。"
    if not results:
        conclusion = "暂无检测数据"

    # 7. Create Report
    report_no = generate_report_no(db)
    
    report = Report(
        report_no=report_no,
        task_id=task.id,
        sample_id=task.sample_id,
        sample_no=sample.sample_no if sample else "",
        sample_name=sample.name if sample else "",
        customer_name=sample.customer_name if sample else "",
        test_items=task.test_items,
        test_results=json.dumps(results_list, ensure_ascii=False),
        conclusion=conclusion,
        template_id=request.template_id,
        prepared_by=current_user.id,
        prepared_by_name=current_user.username,
        prepared_at=datetime.now(),
        status="待审核"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    logger.info(f"Report generated: {report.report_no} from task {task.task_no}")
    return report


# ==================== 报告管理 ====================

@router.get("/", response_model=ReportList)
def get_reports(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    task_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报告列表"""
    query = db.query(Report)
    
    if task_id:
        query = query.filter(Report.task_id == task_id)
    if status:
        query = query.filter(Report.status == status)
    if keyword:
        query = query.filter(
            (Report.report_no.contains(keyword)) |
            (Report.sample_name.contains(keyword)) |
            (Report.customer_name.contains(keyword))
        )
    
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": reports
    }


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(
    report_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报告详情"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 获取审核记录
    audits = db.query(ReportAudit).filter(
        ReportAudit.report_id == report_id
    ).order_by(ReportAudit.audit_level).all()
    
    return {
        "report": report,
        "audits": audits
    }


@router.post("/", response_model=ReportResponse)
def create_report(
    report_create: ReportCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建报告"""
    report_no = generate_report_no(db)
    
    report = Report(
        report_no=report_no,
        **report_create.model_dump(),
        prepared_by_name=current_user.username,
        prepared_at=datetime.now(),
        status="待审核"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    logger.info(f"Report created: {report.report_no} by {current_user.username}")
    return report


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int, 
    report_update: ReportUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新报告"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.status == "已签发":
        raise HTTPException(status_code=400, detail="已签发报告不能修改")
    
    update_data = report_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除报告"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.status == "已签发":
        raise HTTPException(status_code=400, detail="已签发报告不能删除")
    
    db.delete(report)
    db.commit()
    
    logger.info(f"Report deleted: {report.report_no} by {current_user.username}")
    return {"message": "删除成功"}


# ==================== 报告审核 ====================

@router.post("/{report_id}/audit", response_model=ReportAuditResponse)
def audit_report(
    report_id: int,
    audit_create: ReportAuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """审核报告"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.status == "已签发":
        raise HTTPException(status_code=400, detail="报告已签发")
    
    audit = ReportAudit(
        report_id=report_id,
        audit_level=audit_create.audit_level,
        audit_result=audit_create.audit_result,
        audit_opinion=audit_create.audit_opinion,
        auditor_name=current_user.username,
        audited_at=datetime.now()
    )
    db.add(audit)
    
    # 更新报告状态
    if audit_create.audit_result == "通过":
        if audit_create.audit_level >= 3:  # 假设三级审核
            report.status = "已签发"
            report.issued_by_name = current_user.username
            report.issued_at = datetime.now()
        else:
            report.status = "审核中"
    else:
        report.status = "已退回"
    
    db.commit()
    db.refresh(audit)
    
    logger.info(f"Report audited: {report.report_no}, result: {audit_create.audit_result} by {current_user.username}")
    return audit


@router.post("/{report_id}/issue")
def issue_report(
    report_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """签发报告"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.status != "审核中":
        raise HTTPException(status_code=400, detail="报告状态不允许签发")
    
    report.status = "已签发"
    report.issued_by_name = current_user.username
    report.issued_at = datetime.now()
    
    db.commit()
    
    logger.info(f"Report issued: {report.report_no} by {current_user.username}")
    return {"message": "签发成功"}


# ==================== 报告模板 ====================

@router.get("/templates/", response_model=ReportTemplateList)
def get_templates(
    skip: int = 0,
    limit: int = 10,
    template_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报告模板列表"""
    query = db.query(ReportTemplate).filter(ReportTemplate.is_active == True)
    
    if template_type:
        query = query.filter(ReportTemplate.template_type == template_type)
    
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": templates
    }


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报告模板详情"""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.post("/templates/", response_model=ReportTemplateResponse)
def create_template(
    template_create: ReportTemplateCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建报告模板"""
    template = ReportTemplate(
        **template_create.model_dump(),
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    logger.info(f"Report template created: {template.template_name} by {current_user.username}")
    return template


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
def update_template(
    template_id: int,
    template_update: ReportTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新报告模板"""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.put("/templates/{template_id}/default")
def set_default_template(
    template_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.query(ReportTemplate).update({ReportTemplate.is_default: False})
    template.is_default = True
    db.commit()
    return {"message": "设置成功"}


# ==================== 报告统计 ====================

@router.get("/statistics/")
def get_report_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报告统计数据"""
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == "待审核").count()
    auditing = db.query(Report).filter(Report.status == "审核中").count()
    issued = db.query(Report).filter(Report.status == "已签发").count()
    returned = db.query(Report).filter(Report.status == "已退回").count()
    
    return {
        "total": total,
        "pending": pending,
        "auditing": auditing,
        "issued": issued,
        "returned": returned
    }
