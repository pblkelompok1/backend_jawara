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
    if filters.occupation:
        query_filters.append(ResidentModel.occupation == filters.occupation)

    # Keyset pagination: ambil data dengan id > last_id
    if last_id:
        query_filters.append(ResidentModel.resident_id > last_id)

    # Query utama dengan selective eager loading
    query = db.query(ResidentModel).options(
        joinedload(ResidentModel.user_rel),
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

#######################
###  Family Service ###
#######################

def get_family_id_name_list(db: Session, name: str | None = None):
    query = db.query(FamilyModel.family_id, FamilyModel.family_name)
    if name:
        name_filter = name.strip()
        if name_filter:
            query = query.filter(FamilyModel.family_name.ilike(f"%{name_filter}%"))
    families = query.all()
    return [
        {
            "family_id": str(f.family_id),
            "family_name": f.family_name
        }
        for f in families
    ]
    
    
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
