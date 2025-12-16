from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Header, File, UploadFile
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from src.resident.schemas import (
    ResidentList, ResidentsFilter, ResidentMeUpdate, ResidentUpdate, 
    FamilyListResponse, UserListFilter, UserListResponse, UserRegistrationItem
)
from src.resident.service import (
    get_resident_summary, get_residents, change_user_status, get_pending_user,
    get_family_id_name_list, get_occupation_id_name_list, get_user_list
)
from src.entities.resident import ResidentModel
from src.auth.service import get_current_user
from src.auth.schemas import TokenData
from src.entities.user import UserModel
from pathlib import Path
from uuid import uuid4


router = APIRouter(
    prefix='/resident',
    tags=['Resident Service'],
)

utilsRouter = APIRouter(
    prefix='/resident-utils',
    tags=['Resident Utils Service'],
)


#######################
### Resident Routes ###
#######################

@router.get("/list", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=70, seconds=60))])
async def list_residents(
    filters: ResidentsFilter = Depends(),
    db: Session = Depends(get_db)
):
    total, results = get_residents(db=db, filters=filters)

    data = [
        ResidentList(
            resident_id=str(r.resident_id),
            nik=r.nik,
            name=r.name,
            phone=r.phone,
            place_of_birth=r.place_of_birth,
            date_of_birth=str(r.date_of_birth),
            gender=r.gender,
            is_deceased=r.is_deceased,
            family_role=r.family_role,
            religion=r.religion,
            domicile_status=r.domicile_status,
            status=r.status,
            blood_type=r.blood_type,
            profile_img_path=r.profile_img_path,
            ktp_path=r.ktp_path,
            kk_path=r.kk_path,
            birth_certificate_path=r.birth_certificate_path,
            occupation_id=r.occupation_id,
            occupation_name=r.occupation_rel.occupation_name if r.occupation_rel else None,
            family_id=str(r.family_id)
        )
        for r in results
    ]

    return {
        "total": total,
        "limit": filters.limit,
        "offset": filters.offset,
        "data": data
    }
    

@router.get("/summary", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=30, seconds=60))])
async def resident_summary(db: Session = Depends(get_db)):
    return get_resident_summary(db)


# (Admin/RT/Secretary) For approving resident sign-up requests
@router.put("/accept/{user_id}", response_model=dict)
async def accept_user_sign_up(user_id: str, db: Session = Depends(get_db), status: str = "active"):
    change_user_status(db=db, user_id=user_id, status=status)
    return {"detail": f"Update resident {user_id} : Successfully changed status to {status}."}


@router.put("/decline/{user_id}", response_model=dict)
async def decline_user_sign_up(user_id: str, db: Session = Depends(get_db), status: str = "declined"):
    change_user_status(db=db, user_id=user_id, status=status)
    return {"detail": f"Update resident {user_id} : Successfully changed status to {status}."}


@router.get("/request_signup_list", response_model=dict)
async def get_pending_user_signups(
    db: Session = Depends(get_db),
):
    return get_pending_user(db=db)


@router.get("/users/list", response_model=UserListResponse, dependencies=[Depends(SafeRateLimiter(times=50, seconds=60))])
async def list_user_registrations(
    filters: UserListFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get user list with resident data for registration management"""
    total, users = get_user_list(
        db=db,
        status=filters.status,
        role=filters.role,
        limit=filters.limit,
        offset=filters.offset
    )
    
    return UserListResponse(
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        data=[UserRegistrationItem(**user) for user in users]
    )



######################
###  Family Routes ###
######################


@utilsRouter.get("/family/list", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=50, seconds=60))])
async def list_families_with_name_param(
    name: str = None,
    db: Session = Depends(get_db)
):
    families = get_family_id_name_list(db=db, name=name)
    return {"data": families}



##########################
###  Occupation Routes ###
##########################

@utilsRouter.get("/occupation/list", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=50, seconds=60))])
async def list_occupations_with_name_param(
    name: str = None,
    db: Session = Depends(get_db)
):
    occupations = get_occupation_id_name_list(db=db, name=name)
    return {"data": occupations}



##########################
###  My Resident Data  ###
##########################

@router.get("/me")
async def get_my_resident(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.resident_id:
        raise HTTPException(status_code=404, detail="Resident data not found")

    resident = db.query(ResidentModel).filter(ResidentModel.resident_id == user.resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident data not found")

    return {
        "resident_id": str(resident.resident_id),
        "nik": resident.nik,
        "name": resident.name,
        "phone": resident.phone,
        "place_of_birth": resident.place_of_birth,
        "date_of_birth": str(resident.date_of_birth),
        "gender": resident.gender,
        "is_deceased": resident.is_deceased,
        "family_role": resident.family_role,
        "religion": resident.religion,
        "domicile_status": resident.domicile_status,
        "status": resident.status,
        "blood_type": resident.blood_type,
        "occupation_id": resident.occupation_id,
        "profile_img_path": resident.profile_img_path,
        "ktp_path": resident.ktp_path,
        "kk_path": resident.kk_path,
        "birth_certificate_path": resident.birth_certificate_path,
    }

@router.post("/me/profile-image")
async def upload_my_profile_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) cari user yang login
    user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) pastikan user punya resident_id
    if not getattr(user, "resident_id", None):
        raise HTTPException(status_code=404, detail="User has no resident data")

    # 3) ambil resident
    resident = db.query(ResidentModel).filter(ResidentModel.resident_id == user.resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    # 4) validasi file (opsional tapi bagus)
    ext = Path(file.filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="File must be an image")

    # 5) simpan file ke storage/profile/
    ext = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid4()}{ext}"
    save_dir = Path("storage/profile")
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / filename

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # 6) update path di DB
    resident.profile_img_path = str(save_path).replace("\\", "/")
    db.commit()
    db.refresh(resident)

    return {
        "detail": "Profile image updated",
        "profile_img_path": resident.profile_img_path,
    }


@router.patch("/me")
async def update_my_resident(
    payload: ResidentMeUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.resident_id:
        raise HTTPException(status_code=404, detail="Resident data not found")

    resident = db.query(ResidentModel).filter(ResidentModel.resident_id == user.resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    data = payload.model_dump(exclude_none=True)  # pydantic v2
    # kalau pydantic v1 pakai: payload.dict(exclude_none=True)

    # update hanya field yang ada di request
    for k, v in data.items():
        setattr(resident, k, v)

    db.commit()
    db.refresh(resident)

    return {
        "resident_id": str(resident.resident_id),
        "nik": resident.nik,
        "name": resident.name,
        "phone": resident.phone,
        "place_of_birth": resident.place_of_birth,
        "date_of_birth": str(resident.date_of_birth),
        "gender": resident.gender,
        "is_deceased": resident.is_deceased,
        "family_role": resident.family_role,
        "religion": resident.religion,
        "domicile_status": resident.domicile_status,
        "status": resident.status,
        "blood_type": resident.blood_type,
        "occupation_id": resident.occupation_id,
        "profile_img_path": resident.profile_img_path,
        "ktp_path": resident.ktp_path,
        "kk_path": resident.kk_path,
        "birth_certificate_path": resident.birth_certificate_path,
    }


##################################
### Update Resident by ID (Admin)
##################################

@router.put("/{resident_id}")
async def update_resident_by_id_endpoint(
    resident_id: str,
    payload: ResidentUpdate,
    db: Session = Depends(get_db),
):
    """Update resident by ID (for admin/RT)"""
    from src.resident.service import update_resident_by_id
    from src.resident.schemas import ResidentUpdate
    
    try:
        data = payload.model_dump(exclude_none=True)
        resident = update_resident_by_id(db, resident_id, data)
        
        return {
            "resident_id": str(resident.resident_id),
            "nik": resident.nik,
            "name": resident.name,
            "phone": resident.phone,
            "place_of_birth": resident.place_of_birth,
            "date_of_birth": str(resident.date_of_birth),
            "gender": resident.gender,
            "is_deceased": resident.is_deceased,
            "family_role": resident.family_role,
            "religion": resident.religion,
            "domicile_status": resident.domicile_status,
            "status": resident.status,
            "blood_type": resident.blood_type,
            "occupation_id": resident.occupation_id,
            "profile_img_path": resident.profile_img_path,
            "ktp_path": resident.ktp_path,
            "kk_path": resident.kk_path,
            "birth_certificate_path": resident.birth_certificate_path,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating resident: {str(e)}")


@router.put("/{resident_id}/profile")
async def upload_resident_profile_image(
    resident_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload profile image for specific resident (for admin/RT)"""
    from src.resident.service import save_uploaded_file, update_resident_profile_image
    
    try:
        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save file
        image_path = await save_uploaded_file(file, "storage/profile", resident_id)
        
        # Update resident record
        resident = update_resident_profile_image(db, resident_id, image_path)
        
        return {
            "detail": "Profile image updated",
            "profile_img_path": resident.profile_img_path,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading profile image: {str(e)}")


@router.put("/{resident_id}/ktp")
async def upload_resident_ktp_image(
    resident_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload KTP image for specific resident (for admin/RT)"""
    from src.resident.service import save_uploaded_file, update_resident_ktp
    
    try:
        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
            raise HTTPException(status_code=400, detail="File must be an image or PDF")
        
        # Save file
        ktp_path = await save_uploaded_file(file, "storage/ktp", resident_id)
        
        # Update resident record
        resident = update_resident_ktp(db, resident_id, ktp_path)
        
        return {
            "detail": "KTP image updated",
            "ktp_path": resident.ktp_path,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading KTP image: {str(e)}")

