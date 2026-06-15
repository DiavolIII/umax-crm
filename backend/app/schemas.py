from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime, date
from typing import Optional
from enum import Enum

from app.utils.validators import validate_fio, validate_phone, normalize_phone


class RoleEnum(str, Enum):
    admin = "admin"
    senior_manager = "senior_manager"
    manager = "manager"


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    login: str = Field(..., min_length=3, max_length=100)
    role_id: int

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, v: str) -> str:
        if not validate_fio(v):
            raise ValueError("ФИО должно содержать минимум фамилию и имя (кириллица или латиница)")
        return v.strip()


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    login: Optional[str] = Field(None, min_length=3, max_length=100)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=4, max_length=100)

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_fio(v):
            raise ValueError("ФИО должно содержать минимум фамилию и имя")
        return v.strip() if v else v


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    role: str


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    exam_type: str = Field(..., pattern="^(ОГЭ|ЕГЭ)$")
    grade: int = Field(..., ge=9, le=11)
    format: str = Field(..., min_length=1, max_length=50)
    price: int = Field(..., ge=0)
    start_date: Optional[date] = None
    free_seats: int = Field(0, ge=0)
    is_active: Optional[bool] = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    exam_type: Optional[str] = Field(None, pattern="^(ОГЭ|ЕГЭ)$")
    grade: Optional[int] = Field(None, ge=9, le=11)
    format: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[int] = Field(None, ge=0)
    start_date: Optional[date] = None
    free_seats: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True


class SourceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    id: int
    name: str
    color_code: str

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    student_full_name: str = Field(..., min_length=2, max_length=200)
    student_grade: int = Field(..., ge=9, le=11)
    parent_full_name: Optional[str] = Field(None, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    course_id: int
    source_id: int
    status_id: int
    manager_id: int
    next_contact_date: Optional[date] = None
    comment: Optional[str] = None

    @field_validator("student_full_name")
    @classmethod
    def check_student_name(cls, v: str) -> str:
        if not validate_fio(v):
            raise ValueError("ФИО ученика должно содержать минимум фамилию и имя")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: str) -> str:
        if not validate_phone(v):
            raise ValueError("некорректный формат телефона (ожидается +7XXXXXXXXXX)")
        return normalize_phone(v)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    student_full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    student_grade: Optional[int] = Field(None, ge=9, le=11)
    parent_full_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    course_id: Optional[int] = None
    source_id: Optional[int] = None
    status_id: Optional[int] = None
    manager_id: Optional[int] = None
    next_contact_date: Optional[date] = None
    comment: Optional[str] = None

    @field_validator("student_full_name")
    @classmethod
    def check_student_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_fio(v):
            raise ValueError("ФИО ученика должно содержать минимум фамилию и имя")
        return v.strip() if v else v

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not validate_phone(v):
                raise ValueError("некорректный формат телефона")
            return normalize_phone(v)
        return v


class ApplicationResponse(ApplicationBase):
    id: int
    application_number: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    course_name: Optional[str] = None
    source_name: Optional[str] = None
    status_name: Optional[str] = None
    status_color: Optional[str] = None
    manager_name: Optional[str] = None
    is_overdue: bool = False

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    application_id: int
    user_id: int
    user_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RequestFilters(BaseModel):
    search: Optional[str] = None
    status_id: Optional[int] = None
    subject: Optional[str] = None
    source_id: Optional[int] = None
    manager_id: Optional[int] = None
    only_overdue: Optional[bool] = False
    sort_by: Optional[str] = Field("created_at", pattern="^(created_at|next_contact_date)$")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class StatsResponse(BaseModel):
    total: int
    new: int
    in_progress: int
    overdue: int
    enrolled: int
    rejected: int
