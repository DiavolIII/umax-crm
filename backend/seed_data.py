"""
Скрипт начального наполнения базы данных.
Создаёт пользователей, курсы и демо-заявки для тестирования системы.

Запуск (из папки backend):
    python seed_data.py
"""
import sys
import os
from datetime import datetime, date, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Role, Course, Source, Status, Application
from app.auth import get_password_hash

DEMO_USERS = [
    {"full_name": "Администратор Системы", "login": "admin", "password": "admin123", "role": "admin"},
    {"full_name": "Иванова Мария Петровна", "login": "senior", "password": "senior123", "role": "senior_manager"},
    {"full_name": "Петров Алексей Сергеевич", "login": "manager1", "password": "manager123", "role": "manager"},
    {"full_name": "Сидорова Елена Владимировна", "login": "manager2", "password": "manager123", "role": "manager"},
]

DEMO_COURSES = [
    {"name": "Математика ОГЭ — интенсив", "subject": "Математика", "exam_type": "ОГЭ", "grade": 9, "format": "Онлайн", "price": 8500, "free_seats": 12},
    {"name": "Русский язык ОГЭ", "subject": "Русский язык", "exam_type": "ОГЭ", "grade": 9, "format": "Очно", "price": 7200, "free_seats": 8},
    {"name": "Математика ЕГЭ — профиль", "subject": "Математика", "exam_type": "ЕГЭ", "grade": 11, "format": "Смешанный", "price": 12000, "free_seats": 15},
    {"name": "Физика ЕГЭ", "subject": "Физика", "exam_type": "ЕГЭ", "grade": 11, "format": "Онлайн", "price": 10500, "free_seats": 0},
    {"name": "История ОГЭ", "subject": "История", "exam_type": "ОГЭ", "grade": 9, "format": "Очно", "price": 6800, "free_seats": 10},
    {"name": "Английский язык ЕГЭ", "subject": "Английский язык", "exam_type": "ЕГЭ", "grade": 10, "format": "Онлайн", "price": 9500, "free_seats": 3},
]

DEMO_APPLICATIONS = [
    {"student": "Козлов Дмитрий Андреевич", "grade": 9, "phone": "+79001234567", "email": "kozlov@mail.ru", "course": "Математика ОГЭ — интенсив", "source": "Сайт", "status": "Новая", "manager": "Петров Алексей Сергеевич", "days_offset": 3},
    {"student": "Морозова Анна Игоревна", "grade": 11, "phone": "+79007654321", "email": "morozova@gmail.com", "course": "Математика ЕГЭ — профиль", "source": "Telegram", "status": "Ожидает звонка", "manager": "Сидорова Елена Владимировна", "days_offset": -2},
    {"student": "Волков Сергей Николаевич", "grade": 9, "phone": "+79005551122", "email": None, "course": "Русский язык ОГЭ", "source": "Телефон", "status": "Записан на курс", "manager": "Петров Алексей Сергеевич", "days_offset": 5},
    {"student": "Новикова Ольга Петровна", "grade": 11, "phone": "+79003334455", "email": "novikova@yandex.ru", "course": "Физика ЕГЭ", "source": "VK", "status": "Отказ", "manager": "Сидорова Елена Владимировна", "days_offset": 1},
    {"student": "Смирнов Артём Викторович", "grade": 10, "phone": "+79006667788", "email": "smirnov@mail.ru", "course": "Английский язык ЕГЭ", "source": "Рекомендация", "status": "В работе", "manager": "Петров Алексей Сергеевич", "days_offset": -5},
]


def seed():
    from app.db_utils import test_connection
    from app.config import get_settings

    settings = get_settings()
    params = settings.connection_params()
    ok, msg = test_connection(params)
    if not ok:
        print("OSHIBKA: ne udalos' podklyuchit'sya k PostgreSQL")
        print(msg)
        print("\nIsprav'te DB_PASSWORD v backend/.env i vypolnite: python -m scripts init")
        sys.exit(1)

    db = SessionLocal()
    print("=== Napolnenie bazy dannyh Umax CRM ===\n")

    try:
        roles = {r.name: r for r in db.query(Role).all()}
    except Exception as e:
        from app.db_utils import explain_db_error
        print(explain_db_error(e, params))
        print("\nVypolnite: python -m scripts init")
        sys.exit(1)
    if not roles:
        print("ОШИБКА: роли не найдены. Сначала выполните create_db.sql")
        return

    for u in DEMO_USERS:
        existing = db.query(User).filter(User.login == u["login"]).first()
        if not existing:
            user = User(
                full_name=u["full_name"],
                login=u["login"],
                password_hash=get_password_hash(u["password"]),
                role_id=roles[u["role"]].id,
                is_active=True,
            )
            db.add(user)
            print(f"  + пользователь: {u['login']} / {u['password']} ({u['role']})")
        else:
            print(f"  ~ пользователь {u['login']} уже существует")
    db.commit()

    for c in DEMO_COURSES:
        existing = db.query(Course).filter(Course.name == c["name"]).first()
        if not existing:
            course = Course(
                name=c["name"],
                subject=c["subject"],
                exam_type=c["exam_type"],
                grade=c["grade"],
                format=c["format"],
                price=c["price"],
                free_seats=c["free_seats"],
                start_date=date.today() + timedelta(days=14),
                is_active=True,
            )
            db.add(course)
            print(f"  + курс: {c['name']}")
        else:
            print(f"  ~ курс {c['name']} уже существует")
    db.commit()

    counter = db.query(Application).count()
    for i, a in enumerate(DEMO_APPLICATIONS, start=1):
        app_num = f"Z{counter + i:06d}"
        existing = db.query(Application).filter(Application.application_number == app_num).first()
        if existing:
            continue

        course = db.query(Course).filter(Course.name == a["course"]).first()
        source = db.query(Source).filter(Source.name == a["source"]).first()
        status = db.query(Status).filter(Status.name == a["status"]).first()
        manager = db.query(User).filter(User.full_name == a["manager"]).first()

        if course and source and status and manager:
            app = Application(
                application_number=app_num,
                created_at=datetime.now() - timedelta(days=7),
                student_full_name=a["student"],
                student_grade=a["grade"],
                phone=a["phone"],
                email=a["email"],
                course_id=course.id,
                source_id=source.id,
                status_id=status.id,
                manager_id=manager.id,
                next_contact_date=date.today() + timedelta(days=a["days_offset"]),
                comment="Демо-заявка для тестирования",
            )
            db.add(app)
            print(f"  + заявка: {a['student']}")

    db.commit()
    db.close()

    print("\n=== Готово! ===")
    print("\nУчётные записи для входа:")
    print("  admin    / admin123    — администратор")
    print("  senior   / senior123   — старший менеджер")
    print("  manager1 / manager123  — менеджер")
    print("  manager2 / manager123  — менеджер")


if __name__ == "__main__":
    seed()
