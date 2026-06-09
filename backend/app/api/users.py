"""
用户管理 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleBase
import logging
from pydantic import BaseModel

from app.core.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()


class RolePermissionsUpdate(BaseModel):
    permission_ids: List[int]


def build_permission_tree(permissions: List[Permission]) -> List[dict]:
    node_map = {
        p.id: {
            "id": p.id,
            "name": p.name,
            "children": []
        }
        for p in permissions
    }
    roots = []
    for p in permissions:
        if p.parent_id and p.parent_id in node_map:
            node_map[p.parent_id]["children"].append(node_map[p.id])
        else:
            roots.append(node_map[p.id])
    return roots


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/", response_model=UserResponse)
def create_user(
    user_create: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建用户"""
    from app.core.security import get_password_hash
    
    if db.query(User).filter(User.username == user_create.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user = User(
        username=user_create.username,
        password=get_password_hash(user_create.password),
        real_name=user_create.real_name,
        email=user_create.email,
        phone=user_create.phone,
        department=user_create.department,
        position=user_create.position
    )
    
    # 分配角色
    if user_create.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_create.role_ids)).all()
        user.roles = roles
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User created: {user.username} by {current_user.username}")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    update_data = user_update.model_dump(exclude_unset=True, exclude={"role_ids"})
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # 更新角色
    if user_update.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(user_update.role_ids)).all()
        user.roles = roles
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"User updated: {user.username} by {current_user.username}")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    logger.info(f"User deleted: {user.username} by {current_user.username}")
    return {"message": "删除成功"}


@router.get("/roles/", response_model=List[dict])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色列表"""
    roles = db.query(Role).all()
    return [{"id": r.id, "name": r.name, "code": r.code, "description": r.description} for r in roles]


@router.post("/roles/", response_model=dict)
def create_role(
    role_create: RoleBase, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db.query(Role).filter(Role.code == role_create.code).first():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = Role(name=role_create.name, code=role_create.code, description=role_create.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"id": role.id, "name": role.name, "code": role.code, "description": role.description}


@router.get("/permissions/", response_model=dict)
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    permissions = db.query(Permission).order_by(Permission.sort).all()
    return {"items": build_permission_tree(permissions)}


@router.get("/roles/{role_id}/permissions", response_model=dict)
def get_role_permissions(
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"items": [p.id for p in role.permissions]}


@router.put("/roles/{role_id}/permissions", response_model=dict)
def update_role_permissions(
    role_id: int, 
    payload: RolePermissionsUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    permissions = db.query(Permission).filter(Permission.id.in_(payload.permission_ids)).all()
    role.permissions = permissions
    db.commit()
    return {"message": "更新成功"}
