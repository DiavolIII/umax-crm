from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user

def require_role(allowed_roles: list):
    def role_checker(current_user: User = Depends(get_current_user)):
        role_name = current_user.role.name
        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"доступ запрещен. требуется роль: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

admin_required = require_role(["admin"])
senior_manager_or_admin = require_role(["admin", "senior_manager"])
any_authenticated = require_role(["admin", "senior_manager", "manager"])