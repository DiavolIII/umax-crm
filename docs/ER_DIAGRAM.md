# ER-диаграмма базы данных Umax CRM

База данных спроектирована в **3-й нормальной форме (3НФ)**. Каждая сущность хранится в отдельной таблице, связи реализованы через внешние ключи.

## Диаграмма

```mermaid
erDiagram
    roles ||--o{ users : "имеет"
    users ||--o{ applications : "ведёт"
    users ||--o{ application_comments : "пишет"
    courses ||--o{ applications : "выбран в"
    sources ||--o{ applications : "поступила из"
    statuses ||--o{ applications : "имеет"
    applications ||--o{ application_comments : "содержит"

    roles {
        int id PK
        varchar name UK "admin | senior_manager | manager"
    }

    users {
        int id PK
        varchar full_name
        varchar login UK
        varchar password_hash
        int role_id FK
        boolean is_active
        timestamp created_at
    }

    sources {
        int id PK
        varchar name UK "Сайт | Телефон | Telegram | VK"
    }

    statuses {
        int id PK
        varchar name UK
        varchar color_code "HEX-цвет для UI"
    }

    courses {
        int id PK
        varchar name
        varchar subject
        varchar exam_type "ОГЭ | ЕГЭ"
        int grade "9-11"
        varchar format "Онлайн | Очно | Смешанный"
        int price
        date start_date
        int free_seats
        boolean is_active
    }

    applications {
        int id PK
        varchar application_number UK "Z000001"
        timestamp created_at
        varchar student_full_name
        int student_grade "9-11"
        varchar parent_full_name
        varchar phone
        varchar email
        int course_id FK
        int source_id FK
        int status_id FK
        int manager_id FK
        date next_contact_date
        text comment
        timestamp updated_at
    }

    application_comments {
        int id PK
        int application_id FK
        int user_id FK
        text comment
        timestamp created_at
    }
```

## Описание сущностей

| Таблица | Назначение |
|---------|-----------|
| **roles** | Справочник ролей пользователей системы |
| **users** | Менеджеры и администраторы CRM |
| **sources** | Источники поступления заявок |
| **statuses** | Статусы обработки заявок с цветовой индикацией |
| **courses** | Каталог курсов подготовки к ОГЭ/ЕГЭ |
| **applications** | Заявки от родителей и учеников |
| **application_comments** | История комментариев к заявкам |

## Связи

- `users.role_id` → `roles.id` — каждый пользователь имеет одну роль
- `applications.course_id` → `courses.id` — заявка привязана к курсу
- `applications.source_id` → `sources.id` — источник заявки
- `applications.status_id` → `statuses.id` — текущий статус
- `applications.manager_id` → `users.id` — ответственный менеджер
- `application_comments.application_id` → `applications.id` — комментарий к заявке
- `application_comments.user_id` → `users.id` — автор комментария

## Цветовая индикация статусов

| Статус | Цвет | HEX |
|--------|------|-----|
| Новая | Светло-синий | `#e3f2fd` |
| В работе | Светло-оранжевый | `#fff3e0` |
| Ожидает звонка | Жёлтый | `#fff9c4` |
| Записан на курс | Зелёный | `#c8e6c9` |
| Отказ | Серый | `#eeeeee` |
| Просрочена | Красный | `#ffebee` |

## SQL-скрипт

Полный скрипт создания таблиц: [`backend/create_db.sql`](../backend/create_db.sql)
