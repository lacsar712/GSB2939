"""
配置文件
"""
import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "lims_secret_key_2024_very_secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
