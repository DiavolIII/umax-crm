import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, Role, Course, Source, Status, Application
from app.auth import get_password_hash
from datetime import datetime, date
import pandas as pd

def import_all_data():
    db = SessionLocal()
    
    print("начинаю импорт данных...")
    
    roles = db.query(Role).all()
    if not roles:
        print("ошибка: роли не найдены, сначала выполните create_db.sql")
        return
    
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    senior_role = db.query(Role).filter(Role.name == "senior_manager").first()
    manager_role = db.query(Role).filter(Role.name == "manager").first()
    
    users_data = pd.read_excel("data/managers.xlsx")
    for _, row in users_data.iterrows():
        existing = db.query(User).filter(User.login == row['Login']).first()
        if not existing:
            role_name = row['Role']
            role_id = None
            if role_name == "Администратор":
                role_id = admin_role.id if admin_role else 1
            elif role_name == "Старший менеджер":
                role_id = senior_role.id if senior_role else 2
            else:
                role_id = manager_role.id if manager_role else 3
            
            user = User(
                full_name=row['FullName'],
                login=row['Login'],
                password_hash=get_password_hash(str(row['Password'])),
                role_id=role_id,
                is_active=True
            )
            db.add(user)
    db.commit()
    print("импортированы менеджеры")
    
    courses_data = pd.read_excel("data/courses.xlsx")
    for _, row in courses_data.iterrows():
        existing = db.query(Course).filter(Course.name == row['CourseName']).first()
        if not existing:
            course = Course(
                name=row['CourseName'],
                subject=row['Subject'],
                exam_type=row['ExamType'],
                grade=row['Grade'],
                format=row['Format'],
                price=row['Price'],
                start_date=row['StartDate'].date() if pd.notna(row['StartDate']) else None,
                free_seats=row['FreeSeats'],
                is_active=True
            )
            db.add(course)
    db.commit()
    print("импортированы курсы")
    
    sources_data = pd.read_excel("data/sources.xlsx")
    for _, row in sources_data.iterrows():
        existing = db.query(Source).filter(Source.name == row['SourceName']).first()
        if not existing:
            source = Source(name=row['SourceName'])
            db.add(source)
    db.commit()
    print("импортированы источники")
    
    statuses_data = pd.read_excel("data/statuses.xlsx")
    status_color_map = {
        "Новая": "#e3f2fd",
        "В работе": "#fff3e0",
        "Ожидает звонка": "#fff9c4",
        "Записан на курс": "#c8e6c9",
        "Отказ": "#eeeeee",
        "Просрочена": "#ffebee"
    }
    for _, row in statuses_data.iterrows():
        existing = db.query(Status).filter(Status.name == row['StatusName']).first()
        if not existing:
            status = Status(
                name=row['StatusName'],
                color_code=status_color_map.get(row['StatusName'], "#e0e0e0")
            )
            db.add(status)
    db.commit()
    print("импортированы статусы")
    
    applications_data = pd.read_excel("data/applications.xlsx")
    for _, row in applications_data.iterrows():
        course = db.query(Course).filter(Course.name == row['CourseName']).first()
        source = db.query(Source).filter(Source.name == row['Source']).first()
        status = db.query(Status).filter(Status.name == row['Status']).first()
        
        manager_name = row['ManagerFullName']
        manager = db.query(User).filter(User.full_name == manager_name).first()
        
        if course and source and status and manager:
            existing = db.query(Application).filter(Application.application_number == f"Z{int(row['ApplicationID']):06d}").first()
            if not existing:
                next_date = None
                if pd.notna(row['NextContactDate']):
                    next_date = row['NextContactDate'].date() if isinstance(row['NextContactDate'], datetime) else row['NextContactDate']
                
                app = Application(
                    application_number=f"Z{int(row['ApplicationID']):06d}",
                    created_at=row['CreatedAt'] if isinstance(row['CreatedAt'], datetime) else datetime.now(),
                    student_full_name=row['StudentFullName'],
                    student_grade=row['Grade'],
                    parent_full_name=row['ParentFullName'] if pd.notna(row['ParentFullName']) else None,
                    phone=str(row['Phone']),
                    email=row['Email'] if pd.notna(row['Email']) else None,
                    course_id=course.id,
                    source_id=source.id,
                    status_id=status.id,
                    manager_id=manager.id,
                    next_contact_date=next_date,
                    comment=row['Comment'] if pd.notna(row['Comment']) else None
                )
                db.add(app)
    
    db.commit()
    print("импортированы заявки")
    print("импорт завершен")

if __name__ == "__main__":
    import_all_data()