"""
审计追踪模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, comment="操作用户ID")
    user_name = Column(String(50), comment="操作用户名")
    operation_type = Column(String(100), comment="操作类型(登录/新增/修改/删除/导出等)")
    operation_module = Column(String(100), comment="操作模块")
    operation_content = Column(Text, comment="操作内容")
    request_method = Column(String(10), comment="请求方法")
    request_url = Column(String(500), comment="请求URL")
    request_params = Column(Text, comment="请求参数")
    response_code = Column(Integer, comment="响应状态码")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="用户代理")
    duration = Column(Integer, comment="耗时(ms)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
