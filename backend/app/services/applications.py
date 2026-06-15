from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Application, Course, Status

CLOSED_STATUSES = {"Записан на курс", "Отказ"}
OVERDUE_COLOR = "#ffebee"
ENROLLED_STATUS = "Записан на курс"


def is_application_overdue(app: Application) -> bool:
    if not app.next_contact_date:
        return False
    if app.status and app.status.name in CLOSED_STATUSES:
        return False
    return app.next_contact_date < date.today()


def get_display_color(app: Application) -> str:
    if is_application_overdue(app):
        return OVERDUE_COLOR
    return app.status.color_code if app.status else "#eeeeee"


def build_application_response(app: Application):
    from app.schemas import ApplicationResponse

    result = ApplicationResponse.model_validate(app)
    result.course_name = app.course.name if app.course else None
    result.source_name = app.source.name if app.source else None
    result.status_name = app.status.name if app.status else None
    result.status_color = get_display_color(app)
    result.manager_name = app.manager.full_name if app.manager else None
    result.is_overdue = is_application_overdue(app)
    return result


def validate_next_contact(created_at, next_contact_date):
    if next_contact_date and created_at:
        created = created_at.date() if hasattr(created_at, "date") else created_at
        if next_contact_date < created:
            raise HTTPException(
                status_code=400,
                detail="дата следующего контакта не может быть раньше даты создания заявки",
            )


def handle_enrollment(db: Session, course_id: int, status_id: int, previous_status_id: int | None = None):
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status or status.name != ENROLLED_STATUS:
        return

    if previous_status_id == status_id:
        return

    prev = db.query(Status).filter(Status.id == previous_status_id).first() if previous_status_id else None
    if prev and prev.name == ENROLLED_STATUS:
        return

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=400, detail="курс не найден")
    if course.free_seats <= 0:
        raise HTTPException(status_code=400, detail="на курсе нет свободных мест")
    course.free_seats -= 1


def get_stats(db: Session, manager_id: int | None = None) -> dict:
    query = db.query(Application)
    if manager_id:
        query = query.filter(Application.manager_id == manager_id)

    apps = query.all()
    total = len(apps)
    overdue = sum(1 for a in apps if is_application_overdue(a))
    new_count = sum(1 for a in apps if a.status and a.status.name == "Новая")
    enrolled = sum(1 for a in apps if a.status and a.status.name == ENROLLED_STATUS)
    in_progress = sum(1 for a in apps if a.status and a.status.name in {"В работе", "Ожидает звонка"})
    rejected = sum(1 for a in apps if a.status and a.status.name == "Отказ")

    return {
        "total": total,
        "new": new_count,
        "in_progress": in_progress,
        "overdue": overdue,
        "enrolled": enrolled,
        "rejected": rejected,
    }
