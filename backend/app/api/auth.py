"""
认证相关 API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        logger.warning(f"Login failed for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 获取用户权限
    permissions = []
    for role in user.roles:
        for perm in role.permissions:
            permissions.append({
                "id": perm.id,
                "name": perm.name,
                "code": perm.code,
                "type": perm.type,
                "path": perm.path
            })
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone,
            "department": user.department,
            "position": user.position,
            "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in user.roles],
            "permissions": permissions
        }
    }


@router.post("/register", response_model=UserResponse)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_create.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户
    user = User(
        username=user_create.username,
        password=get_password_hash(user_create.password),
        real_name=user_create.real_name,
        email=user_create.email,
        phone=user_create.phone,
        department=user_create.department,
        position=user_create.position
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User registered: {user.username}")
    
    return user
