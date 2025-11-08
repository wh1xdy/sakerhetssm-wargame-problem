from fastapi import FastAPI, Request, Form, status as http_status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiohttp import ClientSession
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

MAIN_APP_URL = "http://127.0.0.1:8081"
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin_secret_key")


@app.get("/unauthorized", response_class=HTMLResponse)
async def admin_home(request: Request):
    return templates.TemplateResponse("unauthorized.html.j2", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    async with ClientSession() as session:
        response = await session.get(
            f"{MAIN_APP_URL}/api/admin/declarations",
            cookies={"admin_key": ADMIN_API_KEY},
        )

        if response.status != 200:
            return templates.TemplateResponse(
                "dashboard.html.j2",
                {
                    "request": request,
                    "error": "Failed to fetch declarations",
                    "declarations": [],
                },
            )

        data = await response.json()
        declarations = data.get("declarations", [])

    return templates.TemplateResponse(
        "dashboard.html.j2",
        {"request": request, "declarations": declarations},
    )


@app.get("/declarations/{declaration_id}", response_class=HTMLResponse)
async def admin_declaration_detail(request: Request, declaration_id: str):
    async with ClientSession() as session:
        response = await session.get(
            f"{MAIN_APP_URL}/api/admin/declarations",
            cookies={"admin_key": ADMIN_API_KEY},
        )

        if response.status != 200:
            return templates.TemplateResponse(
                "error.html.j2",
                {
                    "request": request,
                    "error": "Failed to fetch declaration",
                },
            )

        data = await response.json()
        declarations = data.get("declarations", [])

        declaration = next(
            (d for d in declarations if d["uuid"] == declaration_id), None
        )

        if not declaration:
            return templates.TemplateResponse(
                "error.html.j2",
                {
                    "request": request,
                    "error": f"Declaration with ID {declaration_id} not found",
                },
            )

    return templates.TemplateResponse(
        "declaration_detail.html.j2",
        {"request": request, "declaration": declaration},
    )


@app.post("/declarations/{declaration_id}/status")
async def admin_update_status(
    request: Request, declaration_id: str, status: str = Form(...)
):
    async with ClientSession() as session:
        response = await session.post(
            f"{MAIN_APP_URL}/api/admin/declarations/{declaration_id}/status",
            data={"status": status},
            cookies={"admin_key": ADMIN_API_KEY},
        )

        if response.status != 200:
            error_text = await response.text()
            return templates.TemplateResponse(
                "error.html.j2",
                {
                    "request": request,
                    "error": f"Failed to update declaration status: {error_text}",
                },
            )

    return RedirectResponse(
        url=f"/admin/declarations/{declaration_id}",
        status_code=http_status.HTTP_302_FOUND,
    )
