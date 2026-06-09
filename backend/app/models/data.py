"""
数据管理模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DetectionData(Base):
    """检测数据表"""
    __tablename__ = "detection_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="任务ID")
    sample_id = Column(Integer, ForeignKey("samples.id"), comment="样品ID")
    item_name = Column(String(200), comment="检测项目名称")
    item_code = Column(String(50), comment="检测项目编码")
    result_value = Column(Float, comment="结果值")
    result_unit = Column(String(50), comment="结果单位")
    standard_value = Column(String(100), comment="标准值")
    is_qualified = Column(Boolean, comment="是否合格")
    test_method = Column(String(200), comment="检测方法")
    equipment_id = Column(Integer, comment="使用设备ID")
    equipment_name = Column(String(100), comment="使用设备名称")
    tester_id = Column(Integer, comment="检测人员ID")
    tester_name = Column(String(50), comment="检测人员姓名")
    test_date = Column(DateTime, comment="检测日期")
    environment = Column(String(200), comment="环境条件")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class OriginalRecord(Base):
    """原始记录表"""
    __tablename__ = "original_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_no = Column(String(50), unique=True, nullable=False, comment="记录编号")
    task_id = Column(Integer, ForeignKey("tasks.id"), comment="任务ID")
    sample_id = Column(Integer, ForeignKey("samples.id"), comment="样品ID")
    sample_no = Column(String(50), comment="样品编号")
    sample_name = Column(String(200), comment="样品名称")
    test_items = Column(Text, comment="检测项目")
    record_content = Column(Text, comment="记录内容")
    tester_id = Column(Integer, comment="检测人员ID")
    tester_name = Column(String(50), comment="检测人员姓名")
    test_date = Column(DateTime, comment="检测日期")
    reviewer_id = Column(Integer, comment="复核人ID")
    reviewer_name = Column(String(50), comment="复核人姓名")
    review_date = Column(DateTime, comment="复核日期")
    status = Column(String(50), default="待审核", comment="状态")
    attachment_url = Column(String(500), comment="附件地址")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class DataTrace(Base):
    """数据溯源表"""
    __tablename__ = "data_traces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trace_no = Column(String(50), unique=True, nullable=False, comment="溯源编号")
    sample_id = Column(Integer, comment="样品ID")
    task_id = Column(Integer, comment="任务ID")
    data_id = Column(Integer, comment="数据ID")
    equipment_id = Column(Integer, comment="设备ID")
    reagent_id = Column(Integer, comment="试剂ID")
    trace_type = Column(String(50), comment="溯源类型")
    trace_content = Column(Text, comment="溯源内容")
    operator_id = Column(Integer, comment="操作人ID")
    operator_name = Column(String(50), comment="操作人姓名")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
