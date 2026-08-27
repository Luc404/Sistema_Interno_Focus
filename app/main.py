from fastapi import FastAPI
from app.routers import arquivo_router

app = FastAPI()

app.include_router(arquivo_router.router)