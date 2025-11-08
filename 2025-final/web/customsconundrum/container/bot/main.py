from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from playwright.sync_api import sync_playwright
from threading import Semaphore
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
playwright_semaphore = Semaphore(3)

FLAG = os.getenv("FLAG", "SSM{fake_flag}")
URL = "http://127.0.0.1:8080"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request})


@app.post("/", response_class=HTMLResponse)
def bot(
    request: Request,
    description: str = Form(...),
    item_name: str = Form(...),
    value: str = Form(...),
    category: str = Form(...),
):
    playwright_semaphore.acquire()

    try:
        status = "pending"

        with sync_playwright() as p:
            browser = p.chromium.launch()
            c = browser.new_context()
            page = c.new_page()

            # Register
            page.goto(f"{URL}/register", wait_until="networkidle")
            page.fill('input[name="username"]', os.urandom(16).hex())
            page.fill('input[name="email"]', os.urandom(16).hex() + "@skibidi.gyatt")
            password = os.urandom(16).hex()
            page.fill('input[name="password"]', password)
            page.fill('input[name="password_confirm"]', password)
            page.click('button[type="submit"]')
            page.wait_for_timeout(1000)

            # Create declaration
            page.goto(f"{URL}/declare", wait_until="networkidle")
            page.fill('input[name="entry_date"]', "2025-03-09")
            page.fill('input[name="country_origin"]', "Madagascar")
            page.fill('textarea[name="description"]', description)
            page.fill('input[name="quantity"]', "1")
            page.fill('input[name="item_name"]', item_name)
            page.fill('input[name="value"]', value)
            page.locator('select[name="category"]').select_option(category)
            page.locator('input[type="checkbox"]').check()
            page.click('button[type="submit"]')

            # Wait for it to be approved...
            page.wait_for_timeout(1000)

            # Check declaration status
            page.goto(f"{URL}/api/declaration/latest/status", wait_until="networkidle")
            status = page.inner_text("pre")

            # Goodbye
            browser.close()

        message = ""
        if status == "approved":
            message = "The declaration was approved! Here's your flag: " + FLAG
        elif status == "pending":
            message = "The declaration is still pending..."
        else:
            message = "The declaration was rejected :("

    finally:
        playwright_semaphore.release()

    return templates.TemplateResponse(
        "index.html.j2", {"request": request, "message": message}
    )
