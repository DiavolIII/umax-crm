# Umax CRM — CRM-система образовательного центра «Юмакс»

Единая система управления заявками для подготовки учеников 9–11 классов к ОГЭ и ЕГЭ.

![Python](https://img.shields.io/badge/Python-3.10+-FF6B00)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791)

---

## Содержание

1. [Технологии](#технологии)
2. [Возможности системы](#возможности-системы)
3. [Структура проекта](#структура-проекта)
4. [Быстрый старт](#быстрый-старт)
5. [Полная инструкция по запуску](#полная-инструкция-по-запуску)
6. [Команды python -m](#команды-python--m)
7. [Учётные записи](#учётные-записи)
8. [Роли пользователей](#роли-пользователей)
9. [API-документация](#api-документация)
10. [ER-диаграмма](#er-диаграмма)
11. [Устранение неполадок](#устранение-неполадок)

---

## Технологии

| Компонент | Технология |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| СУБД | PostgreSQL 14+ |
| ORM | SQLAlchemy 2.0 |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (Bearer Token), bcrypt |

---

## Возможности системы

- Авторизация с JWT и ролевым доступом (admin / senior_manager / manager)
- Реестр заявок с цветовой индикацией статусов и просрочек
- Поиск, фильтрация, сортировка заявок
- Дашборд со статистикой (новые, в работе, просроченные, записанные)
- CRUD заявок, комментарии, назначение менеджеров
- Каталог курсов с контролем свободных мест
- Управление пользователями (администратор)
- Импорт из Excel/CSV и экспорт заявок в CSV
- Валидация ФИО, телефона, email, класса, дат
- Бело-оранжевый современный интерфейс

---

## Структура проекта

```
umax_crm/
├── backend/
│   ├── app/
│   │   ├── __main__.py          # python -m app → запуск сервера
│   │   ├── main.py              # FastAPI-приложение
│   │   ├── config.py            # Настройки (Pydantic Settings)
│   │   ├── models.py            # SQLAlchemy ORM-модели
│   │   ├── schemas.py           # Pydantic-схемы с валидацией
│   │   ├── auth.py              # JWT + bcrypt
│   │   ├── database.py          # Подключение к PostgreSQL
│   │   ├── dependencies.py      # Проверка ролей
│   │   ├── routers/             # API-маршруты
│   │   ├── services/            # Бизнес-логика
│   │   └── utils/               # Валидаторы, хелперы
│   ├── scripts/
│   │   └── __main__.py          # python -m scripts → CLI
│   ├── create_db.sql            # SQL-скрипт (3НФ)
│   ├── seed_data.py             # Демо-данные
│   ├── import_data.py           # Импорт из Excel
│   ├── create_sample_excel.py   # Генерация Excel
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── css/style.css            # Бело-оранжевая тема
│   ├── login.html               # Авторизация
│   ├── requests.html            # Заявки + дашборд
│   ├── courses.html             # Курсы
│   ├── users.html               # Пользователи
│   ├── import.html              # Импорт данных
│   └── js/
├── docs/
│   └── ER_DIAGRAM.md            # ER-диаграмма
├── scripts/                     # bat-файлы запуска (Windows)
├── start.bat                    # полный автозапуск
└── README.md
```

---

## Быстрый старт (Windows — bat-файлы)

Дважды щёлкните **`start.bat`** в корне проекта — он установит зависимости, запустит PostgreSQL, создаст БД и откроет сервер.

Или по шагам из папки `scripts/`:

| Файл | Действие |
|------|----------|
| `1_install.bat` | Python venv + pip install |
| `2_start_postgres.bat` | Запуск службы PostgreSQL + проверка подключения |
| `3_init_db.bat` | Создание БД, таблиц и demo-данных |
| `4_seed_data.bat` | Только demo-данные (если таблицы уже есть) |
| `5_run_server.bat` | Запуск сервера http://localhost:8000 |
| `6_stop_server.bat` | Остановка сервера на порту 8000 |
| `check_db.bat` | Проверка подключения к PostgreSQL |

Пароль PostgreSQL в проекте: **`1111`** (файл `backend/.env`).

После запуска: **http://localhost:8000** → `admin` / `admin123`

---

## Быстрый старт (PowerShell)

```powershell
cd backend
copy .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m scripts init
python -m app
```

Браузер → http://localhost:8000 → `admin` / `admin123`

---

## Полная инструкция по запуску

### Шаг 1. Установка PostgreSQL

1. Скачайте с [postgresql.org/download](https://www.postgresql.org/download/)
2. Установите, запомните пароль пользователя `postgres`
3. Убедитесь, что служба PostgreSQL запущена

```powershell
psql -U postgres -c "SELECT version();"
```

### Шаг 2. Создание базы данных

```powershell
psql -U postgres -c "CREATE DATABASE umax_crm;"
psql -U postgres -d umax_crm -f backend\create_db.sql
```

Скрипт создаёт 7 таблиц в 3НФ и заполняет справочники (роли, статусы, источники).

### Шаг 3. Настройка Python-окружения

```powershell
cd backend
copy .env.example .env
```

Отредактируйте `.env` (пароль PostgreSQL по умолчанию — `1111`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=1111
DB_NAME=umax_crm
SECRET_KEY=umax_super_secret_key_change_me_2024
```

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Шаг 4. Наполнение данными

```powershell
python -m scripts init
```

(или `python -m scripts seed`, если таблицы уже созданы)

### Шаг 5. Запуск сервера

```powershell
python -m app
```

Или альтернативно:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Шаг 6. Открытие приложения

| URL | Описание |
|-----|----------|
| http://localhost:8000 | Главная (→ login) |
| http://localhost:8000/login.html | Вход в систему |
| http://localhost:8000/docs | Swagger API |
| http://localhost:8000/health | Health-check |

---

## Команды python -m

Все команды выполняются из папки `backend/`:

| Команда | Описание |
|---------|----------|
| `python -m app` | Запуск сервера (порт 8000) |
| `python -m uvicorn app.main:app --reload` | Запуск с hot-reload |
| `python -m pip install -r requirements.txt` | Установка зависимостей |
| `python -m scripts seed` | Демо-пользователи, курсы, заявки |
| `python -m scripts excel` | Создать Excel в `data/` |
| `python -m scripts import` | Импорт из Excel в БД |

---

## Учётные записи

| Логин | Пароль | Роль |
|-------|--------|------|
| `admin` | `admin123` | Администратор |
| `senior` | `senior123` | Старший менеджер |
| `manager1` | `manager123` | Менеджер |
| `manager2` | `manager123` | Менеджер |

---

## Роли пользователей

| Роль | Возможности |
|------|------------|
| **admin** | Полный доступ: пользователи, курсы, все заявки, импорт |
| **senior_manager** | Все заявки, назначение менеджеров, удаление, контроль просрочек |
| **manager** | Только свои заявки, комментарии, смена статусов |

---

## API-документация

Swagger UI: http://localhost:8000/docs

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/auth/login` | Авторизация |
| GET | `/requests/` | Список заявок (фильтры, сортировка) |
| GET | `/requests/stats/summary` | Статистика |
| GET | `/requests/export/csv` | Экспорт в CSV |
| POST | `/requests/{id}/comments` | Комментарий |
| GET/POST/PUT/DELETE | `/courses/` | CRUD курсов |
| GET/POST/PUT/DELETE | `/users/` | CRUD пользователей |
| POST | `/import/excel` | Импорт Excel/CSV |
| GET | `/import/template/csv` | Шаблон импорта |

---

## ER-диаграмма

Подробная диаграмма: [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md)

7 таблиц в 3НФ: `roles`, `users`, `sources`, `statuses`, `courses`, `applications`, `application_comments`.

---

## Устранение неполадок

### 503 Service Unavailable при входе

База данных недоступна или не инициализирована. Выполните:

```bat
scripts\2_start_postgres.bat
scripts\3_init_db.bat
```

### 500 Internal Server Error при входе

Часто это **старый сервер** на порту 8000. Остановите и перезапустите:

```bat
scripts\6_stop_server.bat
scripts\5_run_server.bat
```

### UnicodeDecodeError / ошибка подключения

На Windows psycopg2 маскирует реальную ошибку. Выполните диагностику:

```powershell
cd backend
python -m scripts check
```

### Неверный пароль PostgreSQL (самая частая причина)

В `backend/.env` должен быть пароль PostgreSQL (по умолчанию в проекте — `1111`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=1111
DB_NAME=umax_crm
```

Затем выполните `scripts\3_init_db.bat` или:

```powershell
python -m scripts init
python -m app
```

### Ошибка подключения к PostgreSQL
```
sqlalchemy.exc.OperationalError: connection refused
```
→ Проверьте, что PostgreSQL запущен (`scripts\2_start_postgres.bat`) и `DB_PASSWORD=1111` в `.env`.

**ModuleNotFoundError: No module named 'app'**
→ Запускайте команды из папки `backend/`.

**Ошибка bcrypt**
```powershell
python -m pip install --upgrade passlib bcrypt
```

**Порт 8000 занят**
```powershell
python -m uvicorn app.main:app --reload --port 8080
```

---

## Дизайн

Бело-оранжевая цветовая схема:
- Основной: `#FF6B00`
- Фон: `#FFF8F3`
- Статусы: синий (новая), жёлтый (ожидает), красный (просрочена), зелёный (записан), серый (отказ)

---

*Проект разработан для образовательного центра «Юмакс».*
