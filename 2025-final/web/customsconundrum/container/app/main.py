from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status as http_status,
    Form,
    Cookie,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse,
    PlainTextResponse,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import marko
import re

from database import get_db, User, Declaration
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_password_hash,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin_secret_key")


def sanitize_markdown(markdown: str):
    sanitized = re.sub(r"<\s*\w+[^>]*>", "", markdown)
    sanitized = re.sub(r"<\s*/?\s*\w+\s*>", "", sanitized)
    return sanitized


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    return templates.TemplateResponse(
        "index.html.j2",
        {"request": request, "user_logged_in": current_user is not None},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if current_user:
        return RedirectResponse(
            url="/declarations", status_code=http_status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "login.html.j2", {"request": request, "user_logged_in": False}
    )


@app.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html.j2",
            {
                "request": request,
                "user_logged_in": False,
                "flash_message": "Invalid username or password",
                "flash_type": "error",
            },
        )

    access_token = create_access_token(data={"sub": user.username})

    response = RedirectResponse(
        url="/declarations", status_code=http_status.HTTP_302_FOUND
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if current_user:
        return RedirectResponse(
            url="/declarations", status_code=http_status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "register.html.j2", {"request": request, "user_logged_in": False}
    )


@app.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html.j2",
            {
                "request": request,
                "user_logged_in": False,
                "flash_message": "Passwords do not match",
                "flash_type": "error",
            },
        )

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html.j2",
            {
                "request": request,
                "user_logged_in": False,
                "flash_message": "Username already exists",
                "flash_type": "error",
            },
        )

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "register.html.j2",
            {
                "request": request,
                "user_logged_in": False,
                "flash_message": "Email already registered",
                "flash_type": "error",
            },
        )

    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.username})

    response = RedirectResponse(
        url="/declarations", status_code=http_status.HTTP_302_FOUND
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=http_status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@app.get("/declarations", response_class=HTMLResponse)
async def declarations_page(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = await get_current_active_user(request, db)
    declarations = (
        db.query(Declaration).filter(Declaration.owner_id == current_user.id).all()
    )
    return templates.TemplateResponse(
        "declarations.html.j2",
        {"request": request, "user_logged_in": True, "declarations": declarations},
    )


@app.get("/declare", response_class=HTMLResponse)
async def declare_page(request: Request, db: Session = Depends(get_db)):
    await get_current_active_user(request, db)
    return templates.TemplateResponse(
        "declare.html.j2", {"request": request, "user_logged_in": True}
    )


@app.post("/declare")
async def create_declaration(
    request: Request,
    db: Session = Depends(get_db),
    entry_date: str = Form(...),
    country_origin: str = Form(...),
    item_name: str = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    value: float = Form(...),
    category: str = Form(...),
    confirm_legal: bool = Form(...),
):
    current_user = await get_current_active_user(request, db)

    if not confirm_legal:
        return templates.TemplateResponse(
            "declare.html.j2",
            {
                "request": request,
                "user_logged_in": True,
                "flash_message": "You must confirm the legal declaration",
                "flash_type": "error",
            },
        )

    # Quick check for automatic rejection
    blacklist = ["weapon", "drug", "alcohol", "firearm", "gun", "explosive", "bomb"]
    declaration_status = "pending"
    if any([word in description.lower() for word in blacklist]):
        declaration_status = "rejected"

    declaration = Declaration(
        entry_date=entry_date,
        country_origin=country_origin,
        item_name=item_name,
        description=marko.convert(sanitize_markdown(description)),
        quantity=quantity,
        value=value,
        category=category,
        owner_id=current_user.id,
        status=declaration_status,
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)

    return RedirectResponse(
        url=f"/declaration/{declaration.uuid}", status_code=http_status.HTTP_302_FOUND
    )


@app.get("/declaration/{declaration_id}", response_class=HTMLResponse)
async def declaration_detail(
    request: Request,
    declaration_id: str,
    db: Session = Depends(get_db),
):
    current_user = await get_current_active_user(request, db)

    declaration = (
        db.query(Declaration)
        .filter(
            Declaration.uuid == declaration_id, Declaration.owner_id == current_user.id
        )
        .first()
    )

    if not declaration:
        return RedirectResponse(
            url="/declarations", status_code=http_status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        "declaration_detail.html.j2",
        {"request": request, "user_logged_in": True, "declaration": declaration},
    )


@app.get("/api/declaration/{declaration_id}/status", response_class=PlainTextResponse)
async def get_declaration_status(
    request: Request,
    declaration_id: str,
    db: Session = Depends(get_db),
):
    current_user = await get_current_active_user(request, db)

    if declaration_id == "latest":
        declaration = (
            db.query(Declaration)
            .filter(Declaration.owner_id == current_user.id)
            .order_by(Declaration.created_at.desc())
            .first()
        )
    else:
        declaration = (
            db.query(Declaration)
            .filter(
                Declaration.uuid == declaration_id,
                Declaration.owner_id == current_user.id,
            )
            .first()
        )

    if not declaration:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Declaration not found or access denied",
        )

    return declaration.status


# ---------- ADMIN API ----------
@app.get("/api/admin/declarations", response_class=JSONResponse)
async def admin_get_declarations(
    request: Request, db: Session = Depends(get_db), admin_key: str = Cookie(None)
):
    if not admin_key or admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    declarations = db.query(Declaration).all()

    return {"declarations": declarations}


@app.post("/api/admin/declarations/{declaration_id}/status")
async def admin_update_declaration_status(
    declaration_id: str,
    status: str = Form(...),
    db: Session = Depends(get_db),
    admin_key: str = Cookie(None),
):
    if not admin_key or admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    declaration = (
        db.query(Declaration).filter(Declaration.uuid == declaration_id).first()
    )
    if not declaration:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Declaration with ID {declaration_id} not found",
        )

    declaration.status = status
    db.commit()

    return {"success": True, "declaration_id": declaration_id, "status": status}
