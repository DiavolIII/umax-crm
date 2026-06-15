from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Course
from app.schemas import CourseCreate, CourseUpdate, CourseResponse
from app.dependencies import admin_required, any_authenticated

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/subjects/list")
def get_subjects(db: Session = Depends(get_db), current_user: User = Depends(any_authenticated)):
    return [s[0] for s in db.query(Course.subject).distinct().all()]


@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    grade: Optional[int] = Query(None, ge=9, le=11),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    query = db.query(Course)
    if subject:
        query = query.filter(Course.subject == subject)
    if exam_type:
        query = query.filter(Course.exam_type == exam_type)
    if grade:
        query = query.filter(Course.grade == grade)
    if is_active is not None:
        query = query.filter(Course.is_active == is_active)
    return query.offset(skip).limit(limit).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="курс не найден")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    new_course = Course(**course_data.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="курс не найден")
    for key, value in course_data.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="курс не найден")
    if course.applications:
        course.is_active = False
        db.commit()
        return {"message": "курс деактивирован, так как есть связанные заявки"}
    db.delete(course)
    db.commit()
    return {"message": "курс удален"}
