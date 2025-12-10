from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import RegisterUserRequest, Token, LoginUserRequest, TokenData
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from .service import check_user_resident_data, get_current_user, is_user_status_pending, login_for_access_token, create_user_in_db, refresh_access_token, revoke_refresh_token, get_user_family_id
from fastapi import File, UploadFile, Form
from src.auth.schemas import ResidentSubmissionRequest
from .service import create_resident_submission_service, decode_token

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
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

        return {"detail": "User registered successfully"}

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
    

@router.get("/check_resident_data")
async def check_is_resident_data_exists(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        has_resident_data = check_user_resident_data(user_id=current_user.user_id, db=db)
        return {"has_resident_data": has_resident_data}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Check failed: " + str(e))
    

@router.get("/check_user_status")
async def check_is_user_pending(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        is_pending = is_user_status_pending(user_id=current_user.user_id, db=db)
        return {"is_pending": is_pending}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Check failed: " + str(e))


@router.get("/family")
async def get_user_family(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get family_id dari user yang sedang login.
    
    User harus memiliki resident_id yang terhubung ke resident,
    dan resident tersebut harus memiliki family_id.
    
    Returns:
        family_id: UUID keluarga user, atau null jika tidak ada
    """
    try:
        family_id = get_user_family_id(user_id=current_user.user_id, db=db)
        return {"family_id": family_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get family: " + str(e))

@router.post("/resident/submissions")
async def create_resident_submission(
    request: Request,
    name: str = Form(...),
    nik: str = Form(...),
    phone: str = Form(None),
    place_of_birth: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    family_role: str = Form(...),
    religion: str = Form(None),
    domicile_status: str = Form(None),
    status: str = "pending",
    blood_type: str = Form(None),
    family_id: str = Form(...),
    occupation_id: int = Form(...),
    ktp_file: UploadFile = File(...),
    kk_file: UploadFile = File(...),
    birth_certificate_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        token = auth_header.split(" ", 1)[1]
        token_data = decode_token(token)
        user_id = token_data.user_id

        resident_data = ResidentSubmissionRequest(
            name=name,
            nik=nik,
            phone=phone,
            place_of_birth=place_of_birth,
            date_of_birth=date_of_birth,
            gender=gender,
            family_role=family_role,
            religion=religion,
            domicile_status=domicile_status,
            status=status,
            blood_type=blood_type,
            family_id=family_id,
            occupation_id=occupation_id
        )
        result = await create_resident_submission_service(
            resident_data,
            ktp_file,
            kk_file,
            birth_certificate_file,
            db,
            user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Submission failed: {str(e)}")
    