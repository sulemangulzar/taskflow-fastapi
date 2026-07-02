from fastapi import FastAPI

from app.api.routes.users import router as auth_router

app = FastAPI(title="TaskFlow API")

app.include_router(auth_router)


@app.get("/")
async def home():
    return {"message": "Welcome to TaskFlow API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
