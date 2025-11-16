from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from auth.model import RegisterUserRequest, Token, LoginUserRequest, TokenData
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from starlette import status
from database.core import get_db
from rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from .service import get_current_user, login_for_access_token, create_user_in_db, refresh_access_token, revoke_refresh_token

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(SafeRateLimiter(times=30, seconds=60))],
)
async def login_user(
    data: LoginUserRequest,
    db: Session = Depends(get_db),
):
    try:
        token = login_for_access_token(
            form_data=OAuth2PasswordRequestForm(
                username=data.email, password=data.password, scope=""
            ),
            db=db
        )
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(SafeRateLimiter(times=10, seconds=60))],
)
async def register_user(
    data: RegisterUserRequest,
    db: Session = Depends(get_db),
):
    try:
        create_user_in_db(
            email=data.email,
            password=data.password,
            role=data.role,
            db=db
        )

        return None

    except Exception as e:
        raise HTTPException(status_code=401, detail=str('Registration failed: ' + str(e)))
    

@router.post("/logout", status_code=200, dependencies=[Depends(SafeRateLimiter(times=10, seconds=60))],)
async def logout_user(
    x_refresh_token: str = Header(..., alias="X-Refresh-Token"),
    db: Session = Depends(get_db)
):
    try:
        revoke_refresh_token(refresh_token=x_refresh_token, db=db)
        return {"detail": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Logout failed: " + str(e))

@router.post("/refresh", response_model=Token)
async def refresh_token(
    x_refresh_token: str = Header(..., alias="X-Refresh-Token"),
    db: Session = Depends(get_db)
):
    try:
        new_token = refresh_access_token(refresh_token=x_refresh_token, db=db)
        return new_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token refresh failed: " + str(e))


@router.post("/me")
async def get_my_profile(current_user: TokenData = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "role": current_user.role
    }