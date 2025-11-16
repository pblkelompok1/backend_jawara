from datetime import timedelta, datetime, timezone
import secrets
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError, decode, ExpiredSignatureError
from sqlalchemy.orm import Session
from entities.user import User
from entities.refresh_session import RefreshSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from exceptions import AppException
from src.auth.schemas import Token, TokenData, RegisterUserRequest
import os
import hashlib

