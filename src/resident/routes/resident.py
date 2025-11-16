from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from auth.schemas import RegisterUserRequest, Token, LoginUserRequest, TokenData
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from starlette import status
from database.core import get_db
from rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/resident',
    tags=['Resident Service'],
)

