import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError

from app.config import get_settings
from app.routers import auth, users, courses, requests, import_export
from app.db_utils import explain_db_error

settings = get_settings()
logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)
logger = logging.getLogger("umax_crm")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CRM-система образовательного центра «Юмакс» — управление заявками, курсами и пользователями",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(x) for x in err.get("loc", []))
        errors.append(f"{field}: {err.get('msg', 'ошибка')}")
    return JSONResponse(status_code=422, content={"detail": "; ".join(errors)})


@app.exception_handler(OperationalError)
async def db_exception_handler(request: Request, exc: OperationalError):
    params = get_settings().connection_params()
    orig = exc.orig if hasattr(exc, "orig") else exc
    detail = explain_db_error(orig, params)
    logger.error("DB error: %s", detail)
    return JSONResponse(status_code=503, content={"detail": detail})


@app.exception_handler(UnicodeDecodeError)
async def unicode_exception_handler(request: Request, exc: UnicodeDecodeError):
    params = get_settings().connection_params()
    detail = explain_db_error(exc, params)
    return JSONResponse(status_code=503, content={"detail": detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    detail = str(exc) if settings.debug else "внутренняя ошибка сервера"
    return JSONResponse(status_code=500, content={"detail": detail})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(requests.router)
app.include_router(import_export.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/api")
def api_root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
def startup_event():
    try:
        from app.database import check_db_on_startup
        check_db_on_startup()
    except Exception as e:
        print(f"WARNING startup: {e}")


frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_path):

    @app.get("/")
    def redirect_to_login():
        return RedirectResponse(url="/login.html")

    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
