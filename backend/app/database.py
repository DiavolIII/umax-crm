import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings
from app.db_utils import get_sqlalchemy_url, test_connection

os.environ.setdefault("PGCLIENTENCODING", "UTF8")

settings = get_settings()
params = settings.connection_params()

try:
    db_url = get_sqlalchemy_url(params)
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
except ImportError as e:
    print(f"WARNING: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


def get_db():
    if SessionLocal is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="База данных недоступна. Запустите scripts\\3_init_db.bat",
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_on_startup() -> bool:
    ok, msg = test_connection(params)
    if ok:
        print("[OK] PostgreSQL podklyuchen")
        return True
    print("\n" + "=" * 55)
    print("  OSHIBKA PODKLYUCHENIYA K POSTGRESQL")
    print("=" * 55)
    print(msg)
    print("=" * 55)
    print("Server zapustitsya, no login ne budet rabotat' do ispravleniya .env\n")
    return False
