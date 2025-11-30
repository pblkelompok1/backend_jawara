from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from src.resident.schemas import ResidentList, ResidentsFilter
from src.resident.service import (
    get_resident_summary, get_residents, change_user_status, get_pending_user,
    get_family_id_name_list, get_occupation_id_name_list
)
from src.entities.resident import ResidentModel


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
            name=r.nik,
            phone=r.phone,
            email=r.user_rel.email if r.user_rel else "",
            date_of_birth=str(r.date_of_birth),
            gender=r.gender,
            is_deceased=r.is_deceased,
            profile_image_url=r.profile_img_path,
            family_name=r.family_rel.family_name if r.family_rel else "",
            religion=r.religion,
            occupation=r.occupation_rel.occupation_name if r.occupation_rel else r.occupation,
            domicile_status=r.domicile_status
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

