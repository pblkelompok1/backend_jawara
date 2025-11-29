from fastapi import FastAPI
from src.auth.controller import router as auth_router
from src.resident.route import router as resident_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(resident_router)