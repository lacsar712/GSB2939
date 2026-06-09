"""
试剂与设备模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base


class Reagent(Base):
    """试剂台账表"""
    __tablename__ = "reagents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reagent_no = Column(String(50), unique=True, nullable=False, comment="试剂编号")
    name = Column(String(200), nullable=False, comment="试剂名称")
    specification = Column(String(100), comment="规格型号")
    manufacturer = Column(String(200), comment="生产厂家")
    batch_no = Column(String(100), comment="批号")
    category = Column(String(100), comment="分类")
    quantity = Column(Float, default=0, comment="库存数量")
    unit = Column(String(20), comment="单位")
    warning_quantity = Column(Float, default=10, comment="预警数量")
    location = Column(String(200), comment="存放位置")
    production_date = Column(Date, comment="生产日期")
    expiry_date = Column(Date, comment="有效期")
    is_expired = Column(Boolean, default=False, comment="是否过期")
    supplier = Column(String(200), comment="供应商")
    price = Column(Float, comment="单价")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Equipment(Base):
    """设备台账表"""
    __tablename__ = "equipments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_no = Column(String(50), unique=True, nullable=False, comment="设备编号")
    name = Column(String(200), nullable=False, comment="设备名称")
    model = Column(String(100), comment="型号")
    manufacturer = Column(String(200), comment="生产厂家")
    serial_no = Column(String(100), comment="序列号")
    category = Column(String(100), comment="分类")
    location = Column(String(200), comment="存放位置")
    purchase_date = Column(Date, comment="购置日期")
    warranty_date = Column(Date, comment="保修截止日期")
    last_calibration_date = Column(Date, comment="上次校准日期")
    next_calibration_date = Column(Date, comment="下次校准日期")
    calibration_organization = Column(String(200), comment="校准机构")
    calibration_result = Column(String(50), comment="校准结果")
    status = Column(String(50), default="正常", comment="状态")
    responsible_person = Column(String(50), comment="负责人")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Consumable(Base):
    """耗材台账表"""
    __tablename__ = "consumables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consumable_no = Column(String(50), unique=True, nullable=False, comment="耗材编号")
    name = Column(String(200), nullable=False, comment="耗材名称")
    specification = Column(String(100), comment="规格型号")
    category = Column(String(100), comment="分类")
    quantity = Column(Float, default=0, comment="库存数量")
    unit = Column(String(20), comment="单位")
    warning_quantity = Column(Float, default=10, comment="预警数量")
    location = Column(String(200), comment="存放位置")
    supplier = Column(String(200), comment="供应商")
    price = Column(Float, comment="单价")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class ConsumableRecord(Base):
    """耗材出入库记录表"""
    __tablename__ = "consumable_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consumable_id = Column(Integer, ForeignKey("consumables.id"), comment="耗材ID")
    consumable_name = Column(String(200), comment="耗材名称")
    record_type = Column(String(50), comment="记录类型(入库/领用/退还)")
    quantity = Column(Float, comment="数量")
    unit = Column(String(20), comment="单位")
    operator_id = Column(Integer, comment="操作人ID")
    operator_name = Column(String(50), comment="操作人姓名")
    department = Column(String(100), comment="部门")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
