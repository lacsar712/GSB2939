# API Package
from fastapi import APIRouter
from . import auth, users, samples, tasks, data, resources, reports, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(samples.router, prefix="/samples", tags=["样品管理"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(data.router, prefix="/data", tags=["数据管理"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源管理"])
api_router.include_router(reports.router, prefix="/reports", tags=["报告管理"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计追踪"])
