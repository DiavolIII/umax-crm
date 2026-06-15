from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse
from app.auth import authenticate_user, create_access_token, get_password_hash
from app.dependencies import admin_required

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.login, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        role=user.role.name
    )

@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    from app.auth import verify_password
    
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="неверный старый пароль")
    
    if len(new_password) < 4:
        raise HTTPException(status_code=400, detail="пароль должен быть не менее 4 символов")
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "пароль успешно изменен"}