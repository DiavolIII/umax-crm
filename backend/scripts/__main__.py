"""CLI-утилиты проекта Umax CRM.

Использование (из папки backend):
    python -m scripts check      — проверить подключение к PostgreSQL
    python -m scripts init       — создать БД, таблицы и демо-данные
    python -m scripts seed       — заполнить БД демо-данными
    python -m scripts excel      — создать Excel-файлы для импорта
    python -m scripts import     — импортировать данные из Excel
"""
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "check":
        from app.config import get_settings
        from app.db_utils import test_connection
        settings = get_settings()
        params = settings.connection_params()
        print(f"Proverka: {params['user']}@{params['host']}:{params['port']}/{params['dbname']}")
        ok, msg = test_connection(params)
        if ok:
            print("OK - podklyuchenie uspeshno!")
        else:
            print(f"OSHIBKA:\n{msg}")
            sys.exit(1)
    elif cmd == "init":
        from init_db import init_all
        init_all()
    elif cmd == "seed":
        from seed_data import seed
        seed()
    elif cmd == "excel":
        import create_sample_excel
    elif cmd == "import":
        from import_data import import_all_data
        import_all_data()
    else:
        print(f"Неизвестная команда: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
