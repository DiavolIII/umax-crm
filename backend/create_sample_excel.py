"""
Генерация Excel-файлов для импорта данных из старой системы.
Создаёт папку data/ с файлами managers.xlsx, courses.xlsx и т.д.

Запуск (из папки backend):
    python create_sample_excel.py
"""
import os
import pandas as pd
from datetime import datetime, date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

pd.DataFrame([
    {"FullName": "Администратор Системы", "Login": "admin", "Password": "admin123", "Role": "Администратор"},
    {"FullName": "Иванова Мария Петровна", "Login": "senior", "Password": "senior123", "Role": "Старший менеджер"},
    {"FullName": "Петров Алексей Сергеевич", "Login": "manager1", "Password": "manager123", "Role": "Менеджер"},
    {"FullName": "Сидорова Елена Владимировна", "Login": "manager2", "Password": "manager123", "Role": "Менеджер"},
]).to_excel(os.path.join(DATA_DIR, "managers.xlsx"), index=False)

pd.DataFrame([
    {"CourseName": "Математика ОГЭ — интенсив", "Subject": "Математика", "ExamType": "ОГЭ", "Grade": 9, "Format": "Онлайн", "Price": 8500, "StartDate": date.today() + timedelta(days=14), "FreeSeats": 12},
    {"CourseName": "Русский язык ОГЭ", "Subject": "Русский язык", "ExamType": "ОГЭ", "Grade": 9, "Format": "Очно", "Price": 7200, "StartDate": date.today() + timedelta(days=21), "FreeSeats": 8},
    {"CourseName": "Математика ЕГЭ — профиль", "Subject": "Математика", "ExamType": "ЕГЭ", "Grade": 11, "Format": "Смешанный", "Price": 12000, "StartDate": date.today() + timedelta(days=7), "FreeSeats": 15},
    {"CourseName": "Физика ЕГЭ", "Subject": "Физика", "ExamType": "ЕГЭ", "Grade": 11, "Format": "Онлайн", "Price": 10500, "StartDate": date.today() + timedelta(days=30), "FreeSeats": 0},
]).to_excel(os.path.join(DATA_DIR, "courses.xlsx"), index=False)

pd.DataFrame([
    {"SourceName": "Сайт"},
    {"SourceName": "Телефон"},
    {"SourceName": "Telegram"},
    {"SourceName": "VK"},
    {"SourceName": "Рекомендация"},
]).to_excel(os.path.join(DATA_DIR, "sources.xlsx"), index=False)

pd.DataFrame([
    {"StatusName": "Новая"},
    {"StatusName": "В работе"},
    {"StatusName": "Ожидает звонка"},
    {"StatusName": "Записан на курс"},
    {"StatusName": "Отказ"},
    {"StatusName": "Просрочена"},
]).to_excel(os.path.join(DATA_DIR, "statuses.xlsx"), index=False)

pd.DataFrame([
    {"ApplicationID": 1, "CreatedAt": datetime.now() - timedelta(days=5), "StudentFullName": "Козлов Дмитрий Андреевич", "Grade": 9, "ParentFullName": "Козлова Ирина Сергеевна", "Phone": "+79001234567", "Email": "kozlov@mail.ru", "CourseName": "Математика ОГЭ — интенсив", "Source": "Сайт", "Status": "Новая", "ManagerFullName": "Петров Алексей Сергеевич", "NextContactDate": date.today() + timedelta(days=3), "Comment": "Заявка с сайта"},
    {"ApplicationID": 2, "CreatedAt": datetime.now() - timedelta(days=3), "StudentFullName": "Морозова Анна Игоревна", "Grade": 11, "ParentFullName": "Морозов Игорь Петрович", "Phone": "+79007654321", "Email": "morozova@gmail.com", "CourseName": "Математика ЕГЭ — профиль", "Source": "Telegram", "Status": "Ожидает звонка", "ManagerFullName": "Сидорова Елена Владимировна", "NextContactDate": date.today() - timedelta(days=2), "Comment": "Просроченный звонок"},
    {"ApplicationID": 3, "CreatedAt": datetime.now() - timedelta(days=10), "StudentFullName": "Волков Сергей Николаевич", "Grade": 9, "ParentFullName": None, "Phone": "+79005551122", "Email": None, "CourseName": "Русский язык ОГЭ", "Source": "Телефон", "Status": "Записан на курс", "ManagerFullName": "Петров Алексей Сергеевич", "NextContactDate": None, "Comment": "Успешно записан"},
]).to_excel(os.path.join(DATA_DIR, "applications.xlsx"), index=False)

print(f"Excel-файлы созданы в {DATA_DIR}/")
print("  managers.xlsx, courses.xlsx, sources.xlsx, statuses.xlsx, applications.xlsx")
print("\nДля импорта выполните: python import_data.py")
