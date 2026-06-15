import os

os.environ.setdefault("PGCLIENTENCODING", "UTF8")


def get_db_driver() -> str:
    """Return available PostgreSQL driver: psycopg or psycopg2."""
    try:
        import psycopg  # noqa: F401
        return "psycopg"
    except ImportError:
        pass
    try:
        import psycopg2  # noqa: F401
        return "psycopg2"
    except ImportError:
        raise ImportError(
            "PostgreSQL driver not found. Run: python -m pip install psycopg[binary]"
        )


def get_sqlalchemy_url(params: dict) -> str:
    driver = get_db_driver()
    return (
        f"postgresql+{driver}://{params['user']}:{params['password']}"
        f"@{params['host']}:{params['port']}/{params['dbname']}?sslmode=disable"
    )


def parse_db_url(url: str) -> dict:
    from urllib.parse import urlparse, unquote
    parsed = urlparse(url.replace("postgresql+psycopg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://"))
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "user": unquote(parsed.username or "postgres"),
        "password": unquote(parsed.password or ""),
        "dbname": parsed.path.lstrip("/") or "umax_crm",
    }


def connect_raw(params: dict, dbname: str | None = None, autocommit: bool = False):
    """Create a raw DB connection using available driver."""
    driver = get_db_driver()
    target_db = dbname or params["dbname"]

    if driver == "psycopg":
        import psycopg
        conninfo = (
            f"host={params['host']} port={params['port']} "
            f"user={params['user']} password={params['password']} "
            f"dbname={target_db} connect_timeout=10 sslmode=disable"
        )
        return psycopg.connect(conninfo, autocommit=autocommit)

    import psycopg2
    conn = psycopg2.connect(
        host=params["host"],
        port=params["port"],
        user=params["user"],
        password=params["password"],
        dbname=target_db,
        connect_timeout=10,
        client_encoding="UTF8",
        sslmode="disable",
    )
    if autocommit:
        conn.autocommit = True
    return conn


def test_connection(params: dict) -> tuple[bool, str]:
    """Test PostgreSQL connection. Returns (success, message)."""
    try:
        conn = connect_raw(params)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
        finally:
            conn.close()
        return True, "OK"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, explain_db_error(e, params)


def explain_db_error(error: Exception, params: dict) -> str:
    if isinstance(error, UnicodeDecodeError):
        return (
            "Oshibka kodirovki pri podklyuchenii k PostgreSQL (Windows).\n"
            f"  1. Prover'te parol v backend/.env\n"
            f"  2. Zapustite: python -m scripts init"
        )

    msg = str(error).lower()
    user = params["user"]
    host = params["host"]
    port = params["port"]
    dbname = params["dbname"]

    if "does not exist" in msg or "ne suschestvuet" in msg or "не существует" in msg:
        if "database" in msg or "baza" in msg or "база" in msg:
            return f"Baza '{dbname}' ne suschestvuet. Vypolnite: python -m scripts init"
        return f"Pol'zovatel '{user}' ne naiden v PostgreSQL."

    if any(x in msg for x in ("password authentication", "пароль", "проверку подлинности", "authentication failed")):
        return (
            f"Nevernyj parol dlya pol'zovatelya '{user}'.\n"
            f"  Otkrojte backend/.env i ukazhite parol:\n"
            f"  DB_PASSWORD=vash_parol\n"
            f"  Zatem: python -m scripts init"
        )

    if any(x in msg for x in (
        "connection refused", "could not connect", "server closed",
        "socket is not connected", "could not receive data", "could not send startup",
    )):
        return (
            f"PostgreSQL ne zapuschen ({host}:{port}).\n"
            f"  1. Win+R -> services.msc -> postgresql -> Zapusk\n"
            f"  2. Prover'te DB_PASSWORD v backend/.env"
        )

    if "timeout" in msg:
        return f"Tajmaut podklyucheniya k {host}:{port}."

    return (
        f"Oshibka podklyucheniya: {error}\n"
        f"  Parametry: {user}@{host}:{port}/{dbname}\n"
        f"  Prover'te backend/.env -> DB_PASSWORD"
    )


def create_database_if_needed(params: dict) -> tuple[bool, str]:
    dbname = params["dbname"]
    try:
        conn = connect_raw(params, dbname="postgres", autocommit=True)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            if cur.fetchone():
                return True, f"Baza '{dbname}' uzhe suschestvuet"
            cur.execute(f'CREATE DATABASE "{dbname}" ENCODING \'UTF8\'')
            cur.close()
        finally:
            conn.close()
        return True, f"Baza '{dbname}' sozdana"
    except Exception as e:
        return False, explain_db_error(e, {**params, "dbname": "postgres"})
