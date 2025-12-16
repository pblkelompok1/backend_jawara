from datetime import timedelta, datetime, timezone
import secrets
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from fastapi import Depends
from passlib.context import CryptContext
from src.exceptions import AppException
from src.entities.resident import ResidentModel
from src.entities.user import UserModel
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from src.resident.schemas import ResidentsFilter
from src.entities.family import FamilyModel

import os
import hashlib

###################
# RESIDENT SERVICES
###################

def get_residents(db, filters: ResidentsFilter, last_id: str | None = None):

    query_filters = []

    # Filter kolom langsung
    if filters.name:
        # gunakan ILIKE, pertimbangkan trigram index di Postgres untuk performa
        query_filters.append(
            ResidentModel.nik.ilike(f"%{filters.name}%") |
            ResidentModel.phone.ilike(f"%{filters.name}%")
        )
    if filters.gender:
        query_filters.append(ResidentModel.gender == filters.gender)
    if filters.is_deceased is not None:
        query_filters.append(ResidentModel.is_deceased == filters.is_deceased)
    if filters.domicile_status:
        query_filters.append(ResidentModel.domicile_status == filters.domicile_status)
    if filters.family_id:
        query_filters.append(ResidentModel.family_id == filters.family_id)

    # Keyset pagination: ambil data dengan id > last_id
    if last_id:
        query_filters.append(ResidentModel.resident_id > last_id)

    # Query utama dengan selective eager loading
    query = db.query(ResidentModel).options(
        joinedload(ResidentModel.user),
        joinedload(ResidentModel.family_rel),
        joinedload(ResidentModel.occupation_rel)
    )

    if query_filters:
        query = query.filter(and_(*query_filters))

    total_subq = db.query(ResidentModel.resident_id)
    if query_filters:
        total_subq = total_subq.filter(and_(*query_filters))
    total_count = total_subq.count()

    results = (
        query
        .order_by(ResidentModel.resident_id)
        .offset(filters.offset)
        .limit(filters.limit)
        .all()
    )

    return total_count, results

def get_resident_summary(db: Session) -> dict:
    total_residents = db.query(ResidentModel).count()
    total_deceased = db.query(ResidentModel).filter(ResidentModel.is_deceased == True).count()
    total_male = db.query(ResidentModel).filter(ResidentModel.gender == "male").count()
    total_female = db.query(ResidentModel).filter(ResidentModel.gender == "female").count()
    
    return {
        "total_residents": total_residents,
        "total_deceased": total_deceased,
        "total_male": total_male,
        "total_female": total_female
    }
    

def change_user_status(db: Session, user_id: str, status: str) -> UserModel:
    try:
        user = db.query(UserModel).filter(UserModel.user_id == user_id).one()
    except NoResultFound:
        raise ValueError(f"User dengan id {user_id} tidak ditemukan.")

    actual_status = str(user.status).strip().lower()
    if actual_status != "pending":
        raise ValueError(f"User dengan id {user_id} tidak berstatus pending. (actual: '{user.status}')")

    user.status = status
    db.commit()
    db.refresh(user)  # refresh agar data terbaru tersedia
    return user


def get_pending_user(db: Session):
    pending_users = db.query(UserModel).filter(UserModel.status == "pending").all()
    return {"pending_users": [
        {
            "user_id": str(u.user_id),
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "resident_id": str(u.resident_id) if u.resident_id else None
        }
        for u in pending_users
    ]}


def get_user_list(db: Session, status: str | None = None, role: str | None = None, limit: int = 20, offset: int = 0):
    """Get user list with resident data for registration approval"""
    from src.entities.home import HomeModel
    from sqlalchemy.orm import joinedload
    
    query = db.query(UserModel).options(
        joinedload(UserModel.resident)
    )
    
    # Apply filters
    if status:
        query = query.filter(UserModel.status == status)
    if role:
        query = query.filter(UserModel.role == role)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    users = query.order_by(UserModel.user_id.desc()).offset(offset).limit(limit).all()
    
    result = []
    for user in users:
        user_data = {
            "user_id": str(user.user_id),
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "name": None,
            "nik": None,
            "phone": None,
            "address": None,
            "family_role": None,
            "ktp_path": None,
            "kk_path": None
        }
        
        # Add resident data if exists
        if user.resident:
            resident = user.resident
            user_data.update({
                "name": resident.name,
                "nik": resident.nik,
                "phone": resident.phone,
                "family_role": resident.family_role,
                "ktp_path": resident.ktp_path,
                "kk_path": resident.kk_path
            })
            
            # Get home address if exists
            home = db.query(HomeModel).filter(HomeModel.family_id == resident.family_id).first()
            if home:
                user_data["address"] = home.home_address
        
        result.append(user_data)
    
    return total, result

#######################
###  Family Service ###
#######################

def get_family_id_name_list(db: Session, name: str | None = None):
    from src.entities.home import HomeModel
    from src.entities.family import RTModel
    from sqlalchemy.orm import joinedload
    
    query = db.query(FamilyModel).options(
        joinedload(FamilyModel.rt_rel)
    )
    
    if name:
        name_filter = name.strip()
        if name_filter:
            query = query.filter(FamilyModel.family_name.ilike(f"%{name_filter}%"))
    
    families = query.all()
    
    result = []
    for f in families:
        # Get head of family (resident with family_role='head')
        head = db.query(ResidentModel).filter(
            ResidentModel.family_id == f.family_id,
            ResidentModel.family_role == "head"
        ).first()
        
        # Get home address
        home = db.query(HomeModel).filter(
            HomeModel.family_id == f.family_id
        ).first()
        
        result.append({
            "family_id": str(f.family_id),
            "family_name": f.family_name,
            "head_of_family": head.name if head else None,
            "address": home.home_address if home else None,
            "rt_name": f.rt_rel.rt_name if f.rt_rel else "Unknown"
        })
    
    return result
    
    
##########################
###  Occupation Service ###
##########################

def get_occupation_id_name_list(db: Session, name: str | None = None):
    from src.entities.resident import OccupationModel
    query = db.query(OccupationModel.occupation_id, OccupationModel.occupation_name)
    if name:
        name_filter = name.strip()
        if name_filter:
            query = query.filter(OccupationModel.occupation_name.ilike(f"%{name_filter}%"))
    occupations = query.all()
    return [
        {
            "occupation_id": str(o.occupation_id),
            "occupation_name": o.occupation_name
        }
        for o in occupations
    ]


##########################
### Update Resident by ID
##########################

def update_resident_by_id(db: Session, resident_id: str, update_data: dict) -> ResidentModel:
    """Update resident by ID (for admin/RT)"""
    from uuid import UUID
    from datetime import datetime
    
    resident = db.query(ResidentModel).filter(
        ResidentModel.resident_id == UUID(resident_id)
    ).first()
    
    if not resident:
        raise ValueError("Resident not found")
    
    # Update only provided fields
    for key, value in update_data.items():
        if value is not None:
            # Convert date_of_birth string to date object if needed
            if key == "date_of_birth" and isinstance(value, str):
                from datetime import date
                value = date.fromisoformat(value)
            setattr(resident, key, value)
    
    db.commit()
    db.refresh(resident)
    return resident


async def save_uploaded_file(file, storage_dir: str, filename_prefix: str = "") -> str:
    """Save uploaded file to storage directory"""
    from pathlib import Path
    from uuid import uuid4
    
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{filename_prefix}_{uuid4()}{file_extension}"
    file_path = storage_path / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return str(file_path).replace("\\", "/")


def update_resident_profile_image(db: Session, resident_id: str, image_path: str) -> ResidentModel:
    """Update resident profile image path"""
    from uuid import UUID
    
    resident = db.query(ResidentModel).filter(
        ResidentModel.resident_id == UUID(resident_id)
    ).first()
    
    if not resident:
        raise ValueError("Resident not found")
    
    resident.profile_img_path = image_path
    db.commit()
    db.refresh(resident)
    return resident


def update_resident_ktp(db: Session, resident_id: str, ktp_path: str) -> ResidentModel:
    """Update resident KTP image path"""
    from uuid import UUID
    
    resident = db.query(ResidentModel).filter(
        ResidentModel.resident_id == UUID(resident_id)
    ).first()
    
    if not resident:
        raise ValueError("Resident not found")
    
    resident.ktp_path = ktp_path
    db.commit()
    db.refresh(resident)
    return resident
