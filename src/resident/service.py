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

    if user.status != "pending":
        raise ValueError(f"User dengan id {user_id} tidak berstatus pending.")

    user.status = status
    db.commit()
    db.refresh(user)  # refresh agar data terbaru tersedia
    return user


def get_pending_user_signups(db: Session):
    pending_users = db.query(ResidentModel.UserModel).filter(ResidentModel.UserModel.status == "pending").all()
    return pending_users
