from datetime import timedelta, datetime, timezone
import secrets
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError, decode, ExpiredSignatureError
from sqlalchemy.orm import Session
from src.entities.user import UserModel
from src.entities.refresh_session import RefreshSessionModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.exceptions import AppException
from src.auth.schemas import Token, TokenData, RegisterUserRequest
import os
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:    
    return bcrypt_context.hash(password)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def authenticate_user(email: str, password: str, db: Session) -> UserModel | bool:
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password_hash(password, user.password_hash):
        raise AppException("Invalid email or password", 401)
    return user


def require_role(*allowed_roles):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise AppException("Forbidden: Insufficient permissions", 403)
    return Depends(role_checker)


def create_access_token(user_id: UUID, role: str, expires_delta: timedelta) -> str:
    expire = datetime.now() + expires_delta
    to_encode = {"sub": str(user_id), "role": role, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id:
            raise AppException("Token invalid", 401)
        return TokenData(user_id=user_id, role=role)
    
    except ExpiredSignatureError:
        raise AppException("Token expired", 401)

    except PyJWTError:
        raise AppException("Invalid token", 401)


def get_current_user(token: str = Depends(oauth2_bearer)) -> TokenData:
    return decode_token(token)


def create_refresh_token(user_id: UUID, db: Session):
    token_plain = secrets.token_urlsafe(64)
    token_hash = hash_refresh_token(token_plain)
    expires_at = datetime.now() + timedelta(days=30)

    refresh_session = RefreshSessionModel(
        user_id=user_id,
        refresh_token_hash=token_hash,
        expires_at=expires_at,
        created_at=datetime.now(),
        revoked=False
    )
    db.add(refresh_session)
    db.commit()

    return token_plain


def revoke_refresh_token(refresh_token: str, db: Session) -> None: 
    token_hash = hash_refresh_token(refresh_token)
    session = db.query(RefreshSessionModel).filter_by(refresh_token_hash=token_hash, revoked=False).first()
    if not session:
        raise AppException("Refresh token not found or already revoked", 401)
    
    session.revoked = True
    db.commit()



def refresh_access_token(refresh_token: str, db: Session) -> Token:
    token_hash = hash_refresh_token(refresh_token)
    session = db.query(RefreshSessionModel).filter_by(refresh_token_hash=token_hash, revoked=False).first()
    if not session:
        raise AppException("Invalid refresh token", 401)
    
    if datetime.now() > session.expires_at:
        raise AppException("Refresh token expired", 401)


    user = db.query(UserModel).filter(UserModel.user_id == session.user_id).first()
    if not user:
        raise AppException("User not found", 401)

    access_token = create_access_token(user_id=user.user_id, role=user.role, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")



def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        user_id=user.user_id,
        role=user.role,  # Role handling can be added here
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, refresh_token=create_refresh_token(user.user_id, db), token_type="bearer")



def create_user_in_db(email: str, password: str, role: str, db: Session) -> str:
    existing_user = db.query(UserModel).filter(UserModel.email == email).first()
    if existing_user:
        raise AppException("Email already registered", 400)
    
    hashed_password = get_password_hash(password)
    new_user = UserModel(
        email=email,
        password_hash=hashed_password,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return "User created successfully"