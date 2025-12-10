# main.py
from fastapi import FastAPI
import asyncio
from src.rate_limit import init_rate_limit
from src.exceptions import AppException, app_exception_handler
from src.api import register_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Izinkan semua origin
    allow_credentials=True,
    allow_methods=["*"],      # Izinkan semua HTTP methods (GET, POST, OPTIONS, dll)
    allow_headers=["*"],      # Izinkan semua headers
)

@app.on_event("startup")
async def startup_event():
	# Initialize rate limiter during application startup (async-safe)
	redis_url = "redis://localhost:6379"
	await init_rate_limit(redis_url)


register_routes(app)