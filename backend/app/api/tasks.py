"""
任务管理 API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.task import Task, TaskAssignment, StandardMethod
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskDetailResponse,
    StandardMethodCreate, StandardMethodResponse, StandardMethodListResponse,
    TaskAssignmentCreate, TaskAssignmentResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def generate_task_no(db: Session) -> str:
    """生成任务编号"""
    today = datetime.now().strftime("%Y%m%d")
    last_task = db.query(Task).filter(
        Task.task_no.like(f"TK{today}%")
    ).order_by(Task.task_no.desc()).first()
    
    if last_task:
        try:
            last_seq = int(last_task.task_no[-4:])
            return f"TK{today}{str(last_seq + 1).zfill(4)}"
        except ValueError:
            pass
            
    return f"TK{today}0001"


@router.get("/", response_model=TaskListResponse)
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    department: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务列表"""
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if department:
        query = query.filter(Task.department == department)
    if keyword:
        query = query.filter(
            (Task.task_no.contains(keyword)) |
            (Task.sample_name.contains(keyword))
        )
    
    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return TaskListResponse(
        total=total,
        items=[TaskResponse.model_validate(t) for t in tasks]
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取分配记录
    assignments = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id
    ).all()
    
    return {
        "task": task,
        "assignments": assignments
    }


@router.post("/", response_model=TaskResponse)
def create_task(
    task_create: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建任务"""
    task_no = generate_task_no(db)
    
    task = Task(
        task_no=task_no,
        sample_id=task_create.sample_id,
        sample_no=task_create.sample_no,
        sample_name=task_create.sample_name,
        test_items=task_create.test_items,
        standard_method_id=task_create.standard_method_id,
        priority=task_create.priority,
        deadline=task_create.deadline,
        department=task_create.department,
        remarks=task_create.remarks,
        status="待分配"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(f"Task created: {task.task_no} by {current_user.username}")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    logger.info(f"Task updated: {task.task_no} by {current_user.username}")
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    
    logger.info(f"Task deleted: {task.task_no} by {current_user.username}")
    return {"message": "删除成功"}


# ==================== 任务分配 ====================

@router.post("/{task_id}/assign", response_model=TaskAssignmentResponse)
def assign_task(
    task_id: int, 
    assignment: TaskAssignmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """分配任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task_assignment = TaskAssignment(
        task_id=task_id,
        user_id=assignment.user_id,
        user_name=assignment.user_name,
        department=assignment.department,
        remarks=assignment.remarks,
        status="待接收",
        assigned_by_name=current_user.username
    )
    
    # 更新任务状态
    task.status = "已分配"
    task.assignee_id = assignment.user_id
    task.assignee_name = assignment.user_name
    
    db.add(task_assignment)
    db.commit()
    db.refresh(task_assignment)
    
    return task_assignment


@router.post("/assignments/{assignment_id}/accept")
def accept_assignment(
    assignment_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """接收任务"""
    assignment = db.query(TaskAssignment).filter(
        TaskAssignment.id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="分配记录不存在")
    
    # 验证是否为当前用户
    if assignment.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="只能接收分配给自己的任务")

    assignment.status = "进行中"
    assignment.accepted_at = datetime.now()
    
    # 更新任务状态
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if task:
        task.status = "进行中"
    
    db.commit()
    
    return {"message": "任务已接收"}


# ==================== 标准方法管理 ====================

@router.get("/methods/", response_model=StandardMethodListResponse)
def get_standard_methods(
    skip: int = 0,
    limit: int = 10,
    standard_type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取标准方法列表"""
    query = db.query(StandardMethod).filter(StandardMethod.is_active == True)
    
    if standard_type:
        query = query.filter(StandardMethod.standard_type == standard_type)
    if keyword:
        query = query.filter(
            (StandardMethod.method_no.contains(keyword)) |
            (StandardMethod.method_name.contains(keyword))
        )
    
    total = query.count()
    methods = query.offset(skip).limit(limit).all()
    
    return StandardMethodListResponse(
        total=total,
        items=[StandardMethodResponse.model_validate(m) for m in methods]
    )


@router.get("/methods/{method_id}", response_model=StandardMethodResponse)
def get_standard_method(
    method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取标准方法详情"""
    method = db.query(StandardMethod).filter(StandardMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="标准方法不存在")
    return method


@router.post("/methods/", response_model=StandardMethodResponse)
def create_standard_method(
    method_create: StandardMethodCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建标准方法"""
    method = StandardMethod(**method_create.model_dump())
    db.add(method)
    db.commit()
    db.refresh(method)
    return method


@router.get("/statistics/")
def get_task_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务统计数据"""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "待分配").count()
    assigned = db.query(Task).filter(Task.status == "已分配").count()
    in_progress = db.query(Task).filter(Task.status == "进行中").count()
    completed = db.query(Task).filter(Task.status == "已完成").count()
    overdue = db.query(Task).filter(
        Task.deadline < datetime.now(),
        Task.status.notin_(["已完成", "已终止"])
    ).count()
    
    return {
        "total": total,
        "pending": pending,
        "assigned": assigned,
        "waiting": assigned,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue
    }
