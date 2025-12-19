from fastapi import FastAPI
from src.auth.controller import router as auth_router
from src.finance.controller import router as finance_router
from src.resident.controller import router as resident_router
from src.resident.controller import utilsRouter as resident_utils_router
from src.ai.controller import router as ai_router
from src.activity.controller import router as activity_router
from src.marketplace.controller import router as marketplace_router
from src.report.controller import router as report_router
from src.letter.controller import router as letter_router
from src.family.controller import router as family_router
from src.home.controller import router as home_router
from src.admin.controller import router as admin_router
from .file_controller import router as file_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(finance_router)
    app.include_router(resident_router)
    app.include_router(resident_utils_router)
    app.include_router(family_router)
    app.include_router(home_router)
    app.include_router(marketplace_router)
    app.include_router(activity_router)
    app.include_router(report_router)
    app.include_router(letter_router)
    app.include_router(ai_router)
    app.include_router(file_router) 