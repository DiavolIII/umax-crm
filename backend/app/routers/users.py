from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Role
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.auth import get_password_hash
from app.dependencies import admin_required

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/roles/list")
def get_roles(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return [{"id": r.id, "name": r.name} for r in db.query(Role).all()]


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        data = UserResponse.model_validate(user)
        data.role_name = user.role.name
        result.append(data)
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    result = UserResponse.model_validate(user)
    result.role_name = user.role.name
    return result


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    if db.query(User).filter(User.login == user_data.login).first():
        raise HTTPException(status_code=400, detail="пользователь с таким логином уже существует")
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="роль не найдена")

    new_user = User(
        full_name=user_data.full_name,
        login=user_data.login,
        password_hash=get_password_hash(user_data.password),
        role_id=user_data.role_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    result = UserResponse.model_validate(new_user)
    result.role_name = role.name
    return result


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="пользователь не найден")

    if user_data.login:
        existing = db.query(User).filter(User.login == user_data.login, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="логин уже используется")
        user.login = user_data.login
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.role_id:
        role = db.query(Role).filter(Role.id == user_data.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="роль не найдена")
        user.role_id = user_data.role_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)

    db.commit()
    db.refresh(user)
    result = UserResponse.model_validate(user)
    result.role_name = user.role.name
    return result


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="нельзя удалить самого себя")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": "пользователь удален"}
