-- ============================================================
-- Umax CRM — SQL-скрипт создания бд (3НФ)
-- Образовательный центр «Юмакс»
-- Запуск: psql -U postgres -d umax_crm -f create_db.sql
-- ============================================================

-- таблица ролей
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- таблица пользователей (менеджеров)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    login VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица источников заявок
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- таблица статусов заявок
CREATE TABLE IF NOT EXISTS statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color_code VARCHAR(20) DEFAULT '#gray'
);

-- таблица курсов
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    exam_type VARCHAR(20) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade >= 9 AND grade <= 11),
    format VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    start_date DATE,
    free_seats INTEGER NOT NULL DEFAULT 0 CHECK (free_seats >= 0),
    is_active BOOLEAN DEFAULT true
);

-- таблица заявок
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    application_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    student_full_name VARCHAR(200) NOT NULL,
    student_grade INTEGER NOT NULL CHECK (student_grade >= 9 AND student_grade <= 11),
    parent_full_name VARCHAR(200),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(200),
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    status_id INTEGER NOT NULL REFERENCES statuses(id) ON DELETE RESTRICT,
    manager_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    next_contact_date DATE,
    comment TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица комментариев (историия)
CREATE TABLE IF NOT EXISTS application_comments (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- индексы для производительности
CREATE INDEX idx_applications_status ON applications(status_id);
CREATE INDEX idx_applications_manager ON applications(manager_id);
CREATE INDEX idx_applications_course ON applications(course_id);
CREATE INDEX idx_applications_created ON applications(created_at);
CREATE INDEX idx_applications_next_contact ON applications(next_contact_date);
CREATE INDEX idx_applications_student_name ON applications(student_full_name);
CREATE INDEX idx_applications_phone ON applications(phone);
CREATE INDEX idx_applications_email ON applications(email);

-- начальные данные ролей
INSERT INTO roles (name) VALUES ('admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('senior_manager') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('manager') ON CONFLICT (name) DO NOTHING;

-- начальные данные статусов
INSERT INTO statuses (name, color_code) VALUES 
    ('Новая', '#e3f2fd'),
    ('В работе', '#fff3e0'),
    ('Ожидает звонка', '#fff9c4'),
    ('Записан на курс', '#c8e6c9'),
    ('Отказ', '#eeeeee'),
    ('Просрочена', '#ffebee')
ON CONFLICT (name) DO NOTHING;

-- начальные данные источников
INSERT INTO sources (name) VALUES 
    ('Сайт'),
    ('Телефон'),
    ('Telegram'),
    ('VK'),
    ('Рекомендация')
ON CONFLICT (name) DO NOTHING;