from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date
import io
import csv

from app.database import get_db
from app.models import User, Application, Status, Course, Source, ApplicationComment, Role
from app.schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    CommentCreate, CommentResponse, RequestFilters, StatsResponse,
)
from app.dependencies import any_authenticated, senior_manager_or_admin
from app.utils.helpers import generate_application_number
from app.services.applications import (
    build_application_response,
    validate_next_contact,
    handle_enrollment,
    get_stats,
    is_application_overdue,
)

router = APIRouter(prefix="/requests", tags=["applications"])


def apply_filters(query, filters: RequestFilters):
    if filters.search:
        search = f"%{filters.search}%"
        query = query.filter(
            or_(
                Application.student_full_name.ilike(search),
                Application.phone.ilike(search),
                Application.email.ilike(search),
            )
        )

    if filters.status_id:
        query = query.filter(Application.status_id == filters.status_id)

    if filters.subject:
        query = query.join(Course).filter(Course.subject == filters.subject)

    if filters.source_id:
        query = query.filter(Application.source_id == filters.source_id)

    if filters.manager_id:
        query = query.filter(Application.manager_id == filters.manager_id)

    if filters.only_overdue:
        today = date.today()
        query = query.join(Status).filter(
            Application.next_contact_date < today,
            Status.name.notin_(["Записан на курс", "Отказ"]),
        )

    order_col = (
        Application.next_contact_date
        if filters.sort_by == "next_contact_date"
        else Application.created_at
    )
    query = query.order_by(order_col.asc() if filters.sort_order == "asc" else order_col.desc())
    return query


# --- справочники (до /{id}, чтобы не перехватывались) ---

@router.get("/sources/list")
def get_sources(db: Session = Depends(get_db), current_user: User = Depends(any_authenticated)):
    return [{"id": s.id, "name": s.name} for s in db.query(Source).all()]


@router.get("/statuses/list")
def get_statuses(db: Session = Depends(get_db), current_user: User = Depends(any_authenticated)):
    return [
        {"id": s.id, "name": s.name, "color_code": s.color_code}
        for s in db.query(Status).all()
    ]


@router.get("/managers/list")
def get_managers_list(db: Session = Depends(get_db), current_user: User = Depends(any_authenticated)):
    managers = (
        db.query(User)
        .join(Role)
        .filter(Role.name.in_(["manager", "senior_manager"]), User.is_active.is_(True))
        .all()
    )
    return [{"id": m.id, "full_name": m.full_name} for m in managers]


@router.get("/stats/summary", response_model=StatsResponse)
def get_applications_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    manager_id = current_user.id if current_user.role.name == "manager" else None
    return get_stats(db, manager_id)


@router.get("/export/csv")
def export_applications_csv(
    search: Optional[str] = Query(None),
    status_id: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    source_id: Optional[int] = Query(None),
    manager_id: Optional[int] = Query(None),
    only_overdue: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    filters = RequestFilters(
        search=search, status_id=status_id, subject=subject,
        source_id=source_id, manager_id=manager_id, only_overdue=only_overdue,
        limit=1000, offset=0,
    )
    query = db.query(Application)
    if current_user.role.name == "manager":
        query = query.filter(Application.manager_id == current_user.id)
    query = apply_filters(query, filters)
    apps = query.all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Номер", "Дата", "Ученик", "Класс", "Телефон", "Email",
        "Курс", "Источник", "Статус", "Менеджер", "След. контакт", "Комментарий",
    ])
    for app in apps:
        writer.writerow([
            app.application_number,
            app.created_at.strftime("%d.%m.%Y") if app.created_at else "",
            app.student_full_name,
            app.student_grade,
            app.phone,
            app.email or "",
            app.course.name if app.course else "",
            app.source.name if app.source else "",
            app.status.name if app.status else "",
            app.manager.full_name if app.manager else "",
            app.next_contact_date.strftime("%d.%m.%Y") if app.next_contact_date else "",
            app.comment or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=umax_applications.csv"},
    )


# --- CRUD ---

@router.get("/", response_model=List[ApplicationResponse])
def get_applications(
    search: Optional[str] = Query(None),
    status_id: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    source_id: Optional[int] = Query(None),
    manager_id: Optional[int] = Query(None),
    only_overdue: bool = Query(False),
    sort_by: str = Query("created_at", pattern="^(created_at|next_contact_date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    filters = RequestFilters(
        search=search, status_id=status_id, subject=subject,
        source_id=source_id, manager_id=manager_id, only_overdue=only_overdue,
        sort_by=sort_by, sort_order=sort_order, limit=limit, offset=offset,
    )
    query = db.query(Application)
    if current_user.role.name == "manager":
        query = query.filter(Application.manager_id == current_user.id)
    query = apply_filters(query, filters)
    return [build_application_response(app) for app in query.offset(offset).limit(limit).all()]


@router.get("/{request_id}", response_model=ApplicationResponse)
def get_application(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    app = db.query(Application).filter(Application.id == request_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    if current_user.role.name == "manager" and app.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="доступ только к своим заявкам")
    return build_application_response(app)


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    for entity, msg in [
        (db.query(Course).filter(Course.id == app_data.course_id).first(), "курс не найден"),
        (db.query(Source).filter(Source.id == app_data.source_id).first(), "источник не найден"),
        (db.query(Status).filter(Status.id == app_data.status_id).first(), "статус не найден"),
        (db.query(User).filter(User.id == app_data.manager_id).first(), "менеджер не найден"),
    ]:
        if not entity:
            raise HTTPException(status_code=400, detail=msg)

    if current_user.role.name == "manager" and app_data.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="нельзя назначить заявку другому менеджеру")

    validate_next_contact(date.today(), app_data.next_contact_date)
    handle_enrollment(db, app_data.course_id, app_data.status_id)

    new_app = Application(
        application_number=generate_application_number(db),
        **app_data.model_dump(),
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return build_application_response(new_app)


@router.put("/{request_id}", response_model=ApplicationResponse)
def update_application(
    request_id: int,
    app_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    app = db.query(Application).filter(Application.id == request_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    if current_user.role.name == "manager" and app.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="нельзя редактировать чужие заявки")

    update_data = app_data.model_dump(exclude_unset=True)

    if "next_contact_date" in update_data:
        validate_next_contact(app.created_at, update_data["next_contact_date"])

    if "manager_id" in update_data and current_user.role.name == "manager":
        raise HTTPException(status_code=403, detail="менеджер не может менять ответственного")

    if "manager_id" in update_data and current_user.role.name not in ("admin", "senior_manager"):
        raise HTTPException(status_code=403, detail="только администратор или ст. менеджер могут менять ответственного")

    new_status_id = update_data.get("status_id", app.status_id)
    new_course_id = update_data.get("course_id", app.course_id)
    handle_enrollment(db, new_course_id, new_status_id, app.status_id)

    for key, value in update_data.items():
        setattr(app, key, value)

    db.commit()
    db.refresh(app)
    return build_application_response(app)


@router.delete("/{request_id}")
def delete_application(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(senior_manager_or_admin),
):
    app = db.query(Application).filter(Application.id == request_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    db.delete(app)
    db.commit()
    return {"message": "заявка удалена"}


@router.post("/{request_id}/comments", response_model=CommentResponse)
def add_comment(
    request_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    app = db.query(Application).filter(Application.id == request_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    if current_user.role.name == "manager" and app.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="нельзя комментировать чужие заявки")

    new_comment = ApplicationComment(
        application_id=request_id,
        user_id=current_user.id,
        comment=comment_data.comment,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        id=new_comment.id,
        application_id=new_comment.application_id,
        user_id=new_comment.user_id,
        user_name=current_user.full_name,
        comment=new_comment.comment,
        created_at=new_comment.created_at,
    )


@router.get("/{request_id}/comments", response_model=List[CommentResponse])
def get_comments(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    app = db.query(Application).filter(Application.id == request_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="заявка не найдена")
    if current_user.role.name == "manager" and app.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="нет доступа к комментариям чужой заявки")

    comments = (
        db.query(ApplicationComment)
        .filter(ApplicationComment.application_id == request_id)
        .order_by(ApplicationComment.created_at.desc())
        .all()
    )
    return [
        CommentResponse(
            id=c.id,
            application_id=c.application_id,
            user_id=c.user_id,
            user_name=c.user.full_name if c.user else None,
            comment=c.comment,
            created_at=c.created_at,
        )
        for c in comments
    ]
