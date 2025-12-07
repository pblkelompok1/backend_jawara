from fastapi import FastAPI
from src.auth.controller import router as auth_router
from src.finance.controller import router as finance_router
from src.resident.controller import router as resident_router
from src.resident.controller import utilsRouter as resident_utils_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(finance_router)
    app.include_router(resident_router)
    app.include_router(resident_utils_router)
