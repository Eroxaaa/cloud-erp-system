from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.database import init_db
from app.routes import auth_routes, customer_routes, dashboard_routes, order_routes, product_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_PAGES = {
    "index.html",
    "login.html",
    "dashboard.html",
    "products.html",
    "customers.html",
    "orders.html",
}

app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    description="Cloud-ready ERP/CRM/WMS backend for wholesale clothing operations.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(customer_routes.router)
app.include_router(order_routes.router)
app.include_router(dashboard_routes.router)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/index.html")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{page_name}", include_in_schema=False)
def serve_frontend_page(page_name: str) -> FileResponse:
    if page_name not in FRONTEND_PAGES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    page_path = FRONTEND_DIR / page_name
    if not page_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend page not found",
        )

    return FileResponse(page_path)
