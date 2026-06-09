"""
检验任务模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base


class Task(Base):
    """检验任务表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_no = Column(String(50), unique=True, nullable=False, comment="任务编号")
    sample_id = Column(Integer, ForeignKey("samples.id"), comment="样品ID")
    sample_no = Column(String(50), comment="样品编号")
    sample_name = Column(String(200), comment="样品名称")
    test_items = Column(Text, comment="检测项目(JSON)")
    standard_method_id = Column(Integer, ForeignKey("standard_methods.id"), comment="标准方法ID")
    status = Column(String(50), default="待分配", comment="任务状态")
    priority = Column(String(20), default="普通", comment="优先级")
    deadline = Column(DateTime, comment="截止日期")
    department = Column(String(100), comment="检测科室")
    assignee_id = Column(Integer, comment="负责人ID")
    assignee_name = Column(String(50), comment="负责人姓名")
    progress = Column(Integer, default=0, comment="进度百分比")
    remarks = Column(Text, comment="备注")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    standard_method = relationship("StandardMethod", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task")


class TaskAssignment(Base):
    """任务分配记录表"""
    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="任务ID")
    user_id = Column(Integer, comment="分配给用户ID")
    user_name = Column(String(50), comment="分配给用户姓名")
    department = Column(String(100), comment="科室")
    status = Column(String(50), default="待接收", comment="状态")
    assigned_by = Column(Integer, comment="分配人ID")
    assigned_by_name = Column(String(50), comment="分配人姓名")
    assigned_at = Column(DateTime, default=datetime.now, comment="分配时间")
    accepted_at = Column(DateTime, comment="接收时间")
    completed_at = Column(DateTime, comment="完成时间")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    task = relationship("Task", back_populates="assignments")


class StandardMethod(Base):
    """标准方法表"""
    __tablename__ = "standard_methods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    method_no = Column(String(50), unique=True, nullable=False, comment="方法编号")
    method_name = Column(String(200), nullable=False, comment="方法名称")
    standard_type = Column(String(50), comment="标准类型(国标/行标/企标)")
    standard_no = Column(String(100), comment="标准编号")
    version = Column(String(50), comment="版本号")
    test_items = Column(Text, comment="检测项目(JSON)")
    equipment_required = Column(Text, comment="所需设备(JSON)")
    reagent_required = Column(Text, comment="所需试剂(JSON)")
    description = Column(Text, comment="方法描述")
    attachment_url = Column(String(500), comment="附件地址")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    tasks = relationship("Task", back_populates="standard_method")
