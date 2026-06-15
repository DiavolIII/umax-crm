from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app.database import get_db
from app.models import User, Application, Course, Source, Status
from app.dependencies import admin_required
from app.utils.helpers import generate_application_number

router = APIRouter(prefix="/import", tags=["import-export"])


@router.post("/excel")
async def import_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="поддерживаются файлы .xlsx, .xls, .csv")

    contents = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents), sep=None, engine="python")
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ошибка чтения файла: {e}")

    required = ["StudentFullName", "Grade", "Phone", "CourseName", "Source", "Status"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"отсутствует колонка: {col}")

    created_count = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            course = db.query(Course).filter(Course.name == row.get("CourseName")).first()
            if not course:
                errors.append(f"строка {idx + 2}: курс '{row.get('CourseName')}' не найден")
                continue

            source = db.query(Source).filter(Source.name == row.get("Source")).first() or db.query(Source).first()
            status = db.query(Status).filter(Status.name == row.get("Status")).first() or db.query(Status).first()

            manager_name = row.get("ManagerFullName")
            if manager_name and pd.notna(manager_name):
                manager = db.query(User).filter(User.full_name == manager_name).first()
            else:
                manager = db.query(User).first()
            if not manager:
                errors.append(f"строка {idx + 2}: менеджер не найден")
                continue

            next_contact = None
            if pd.notna(row.get("NextContactDate")):
                val = row["NextContactDate"]
                next_contact = val.date() if isinstance(val, datetime) else pd.to_datetime(val).date()

            db.add(Application(
                application_number=generate_application_number(db),
                student_full_name=str(row["StudentFullName"]),
                student_grade=int(row["Grade"]),
                parent_full_name=str(row["ParentFullName"]) if pd.notna(row.get("ParentFullName")) else None,
                phone=str(row["Phone"]),
                email=str(row["Email"]) if pd.notna(row.get("Email")) else None,
                course_id=course.id,
                source_id=source.id,
                status_id=status.id,
                manager_id=manager.id,
                next_contact_date=next_contact,
                comment=str(row["Comment"]) if pd.notna(row.get("Comment")) else None,
            ))
            created_count += 1
        except Exception as e:
            errors.append(f"строка {idx + 2}: {e}")

    db.commit()
    return {"message": f"импортировано {created_count} заявок", "created": created_count, "errors": errors}


@router.get("/template/csv")
def download_import_template(current_user: User = Depends(admin_required)):
    output = io.StringIO()
    output.write(
        "StudentFullName;Grade;ParentFullName;Phone;Email;CourseName;Source;Status;"
        "ManagerFullName;NextContactDate;Comment\n"
        "Иванов Иван Иванович;9;Иванова Мария;79001234567;ivan@mail.ru;"
        "Математика ОГЭ — интенсив;Сайт;Новая;Петров Алексей Сергеевич;2026-06-20;Тест\n"
    )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=umax_import_template.csv"},
    )
