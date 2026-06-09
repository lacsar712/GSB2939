"""
样品模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SampleStatus(str, enum.Enum):
    """样品状态"""
    PENDING = "待登记"
    REGISTERED = "已登记"
    TESTING = "检测中"
    COMPLETED = "检测完成"
    ARCHIVED = "已归档"


class Sample(Base):
    """样品表"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_no = Column(String(50), unique=True, nullable=False, comment="样品编号")
    name = Column(String(200), nullable=False, comment="样品名称")
    source = Column(String(200), comment="样品来源")
    type = Column(String(100), comment="样品类型")
    batch_no = Column(String(100), comment="批次号")
    quantity = Column(Float, comment="数量")
    unit = Column(String(20), comment="单位")
    status = Column(String(50), default=SampleStatus.PENDING.value, comment="状态")
    customer_name = Column(String(100), comment="客户名称")
    customer_contact = Column(String(100), comment="客户联系人")
    customer_phone = Column(String(50), comment="客户电话")
    receive_date = Column(DateTime, comment="接收日期")
    expected_date = Column(DateTime, comment="预期完成日期")
    remarks = Column(Text, comment="备注")
    storage_id = Column(Integer, ForeignKey("sample_storages.id"), comment="存储位置ID")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    storage = relationship("SampleStorage", back_populates="samples")
    transfers = relationship("SampleTransfer", back_populates="sample")


class SampleStorage(Base):
    """样品存储位置表"""
    __tablename__ = "sample_storages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_code = Column(String(50), unique=True, nullable=False, comment="位置编码")
    location_name = Column(String(100), nullable=False, comment="位置名称")
    location_type = Column(String(50), comment="位置类型(库房/冰箱/货架)")
    parent_id = Column(Integer, comment="父级位置ID")
    capacity = Column(Integer, default=100, comment="容量")
    used_capacity = Column(Integer, default=0, comment="已用容量")
    temperature = Column(String(50), comment="温度要求")
    humidity = Column(String(50), comment="湿度要求")
    status = Column(String(20), default="正常", comment="状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    samples = relationship("Sample", back_populates="storage")


class SampleTransfer(Base):
    """样品流转记录表"""
    __tablename__ = "sample_transfers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False, comment="样品ID")
    from_location = Column(String(100), comment="原位置")
    to_location = Column(String(100), comment="目标位置")
    from_status = Column(String(50), comment="原状态")
    to_status = Column(String(50), comment="目标状态")
    operator_id = Column(Integer, comment="操作人ID")
    operator_name = Column(String(50), comment="操作人姓名")
    operation = Column(String(100), comment="操作类型")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    sample = relationship("Sample", back_populates="transfers")
