from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.config import STATIC_DIR, gemini_enabled
from app.config import SECRET_KEY
from app.csrf import CSRFMiddleware, SecurityHeadersMiddleware
from app.db import SessionLocal
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import marketing as marketing_router
from app.routers import phan_hoi as phan_hoi_router
from app.routers import student as student_router
from app.routers import tai_khoan as tai_khoan_router
from app.routers import teacher as teacher_router
from app.seed import seed_if_empty
from app.templating import templates

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("gals")


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_if_empty()
    if gemini_enabled():
        from app.gemini import resolve_model

        log.info("Gemini: dùng model %s", resolve_model())
    else:
        log.warning(
            "Gemini: chưa có GEMINI_API_KEY — chạy CHẾ ĐỘ DEMO NGOẠI TUYẾN "
            "(AI trả lời bằng kịch bản dựng sẵn, mọi màn hình vẫn bấm được)."
        )
    yield


app = FastAPI(title="GALS", lifespan=lifespan, docs_url=None, redoc_url=None)

# Authlib giữ tham số state của OAuth trong phiên của Starlette. Phiên này
# chỉ dùng cho vòng chuyển hướng đó — việc đăng nhập vẫn nằm ở cookie riêng
# trong app/auth.py.
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax", https_only=False)
app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(teacher_router.router)
app.include_router(chat_router.router)
app.include_router(marketing_router.router)
app.include_router(phan_hoi_router.router)
app.include_router(tai_khoan_router.router)


@app.get("/suc-khoe", include_in_schema=False)
async def suc_khoe() -> JSONResponse:
    """Kiểm tra sức khoẻ: chạm thật vào cơ sở dữ liệu rồi mới báo xanh.

    Một tiến trình còn sống không có nghĩa là ứng dụng còn dùng được — hỏng hay
    gặp nhất là web chạy bình thường còn cơ sở dữ liệu thì không với tới. Nên ở
    đây có một câu truy vấn thật; không chạy được thì trả 503 để nhà cung cấp
    đừng chuyển lưu lượng sang bản triển khai mới, và để máy dò bên ngoài đánh
    thức người thay vì để một thầy cô phát hiện giữa buổi dạy.

    Không chạm vào dữ liệu của ai và không kể gì về bên trong: chỉ "ok" hoặc
    503. Một trang sức khoẻ liệt kê phiên bản thư viện là một trang do thám
    miễn phí.
    """
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        log.exception("Kiểm tra sức khoẻ: không truy vấn được cơ sở dữ liệu")
        return JSONResponse({"trang_thai": "loi"}, status_code=503)
    return JSONResponse({"trang_thai": "ok"})


@app.get("/robots.txt", include_in_schema=False)
async def robots() -> FileResponse:
    """Máy quét tìm /robots.txt ở gốc, không tìm trong /static."""
    return FileResponse(STATIC_DIR / "robots.txt", media_type="text/plain")


@app.exception_handler(404)
async def not_found(request: Request, exc) -> HTMLResponse:
    return templates.TemplateResponse(request, "404.html", status_code=404)
