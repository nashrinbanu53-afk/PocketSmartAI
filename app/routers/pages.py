from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import TEMPLATE_DIR
from ..auth import current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = current_user(request)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user}
    )


@router.get("/testimonials", response_class=HTMLResponse)
def testimonials(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="testimonials.html",
        context={}
    )


@router.get("/history-page", response_class=HTMLResponse)
def history_page(request: Request):
    user = current_user(request)

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"user": user}
    )


@router.get("/recommendations/{recommendation_id}", response_class=HTMLResponse)
def recommendation_page(request: Request, recommendation_id: int):
    user = current_user(request)

    return templates.TemplateResponse(
        request=request,
        name="recommendation.html",
        context={
            "user": user,
            "recommendation_id": recommendation_id
        }
    )


@router.get("/planner/{planner}", response_class=HTMLResponse)
def planner(request: Request, planner: str):

    if planner not in {"home", "party", "jewelry"}:
        raise HTTPException(
            status_code=404,
            detail="Planner not found"
        )

    user = current_user(request)

    return templates.TemplateResponse(
        request=request,
        name=f"{planner}_planner.html",
        context={"user": user}
    )