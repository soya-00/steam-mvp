from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import FIELD_NAME_BY_KEY
from app.scenarios import all_scenarios
from app.templating import templates

router = APIRouter()


@router.get("/kham-pha", response_class=HTMLResponse)
def explore(request: Request, linh_vuc: str = "") -> HTMLResponse:
    chon = linh_vuc if linh_vuc in FIELD_NAME_BY_KEY else ""
    scenarios = all_scenarios()
    if chon:
        name = FIELD_NAME_BY_KEY[chon]
        scenarios = [s for s in scenarios if s.field == name]

    return templates.TemplateResponse(
        request,
        "marketing/kham_pha.html",
        {"user": None, "page": "kham_pha", "danh_sach": scenarios, "chon": chon},
    )


@router.get("/linh-vuc", response_class=HTMLResponse)
def fields(request: Request) -> HTMLResponse:
    tieu_bieu = {}
    for s in all_scenarios():
        tieu_bieu.setdefault(s.field, s)

    return templates.TemplateResponse(
        request,
        "marketing/linh_vuc.html",
        {"user": None, "page": "linh_vuc", "tieu_bieu": tieu_bieu},
    )


@router.get("/ve-chung-toi", response_class=HTMLResponse)
def about(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "marketing/ve_chung_toi.html",
        {"user": None, "page": "ve_chung_toi"},
    )
