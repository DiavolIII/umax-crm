"""
Инициализация бд Umax CRM.
Запуск: python -m scripts init
"""
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.config import get_settings
from app.db_utils import create_database_if_needed, test_connection


def run_sql_script():
    sql_path = os.path.join(ROOT, "create_db.sql")
    if not os.path.exists(sql_path):
        return False, f"File not found: {sql_path}"

    settings = get_settings()
    params = settings.connection_params()

    try:
        from app.db_utils import connect_raw
        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()
        conn = connect_raw(params, autocommit=True)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
        finally:
            conn.close()
        return True, "Tablicy sozdany (create_db.sql)"
    except Exception as e:
        return False, f"Oshibka SQL: {e}"


def init_all():
    print("=== Inicializaciya Umax CRM ===\n")
    settings = get_settings()
    params = settings.connection_params()

    print(f"Podklyuchenie: {params['user']}@{params['host']}:{params['port']}/{params['dbname']}")
    print(f"Parol v .env: {'*' * len(params['password'])}\n")

    print("[1/4] Sozdanie bazy dannyh...")
    ok, msg = create_database_if_needed(params)
    print(f"  {msg}")
    if not ok:
        print("\nNe udalos'. Isprav'te DB_PASSWORD v backend/.env")
        sys.exit(1)

    print("\n[2/4] Sozdanie tablic...")
    ok, msg = run_sql_script()
    print(f"  {msg}")
    if not ok:
        sys.exit(1)

    print("\n[3/4] Proverka podklyucheniya...")
    ok, msg = test_connection(params)
    if ok:
        print("  OK!")
    else:
        print(f"  {msg}")
        sys.exit(1)

    print("\n[4/4] Demo-dannye...")
    from seed_data import seed
    seed()

    print("\n=== Gotovo! ===")
    print("  python -m app")
    print("  http://localhost:8000  |  admin / admin123\n")


if __name__ == "__main__":
    init_all()
