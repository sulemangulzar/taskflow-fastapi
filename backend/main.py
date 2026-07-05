from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.project import router as project_router
from app.api.routes.task import router as task_router

from app.middleware import register_middleware

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
    description="Production API for TaskFlow.",
)

register_middleware(app)

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)


@app.get("/")
async def home():
    return {"message": "Welcome to TaskFlow API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return HTMLResponse(
        """
        <!doctype html>
        <html>
            <head>
                <title>TaskFlow API Docs</title>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
            </head>
            <body>
                <script id="api-reference" data-url="/openapi.json"></script>
                <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
            </body>
        </html>
        """
    )
