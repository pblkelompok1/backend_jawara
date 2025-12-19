from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException
from uuid import UUID
import uuid as uuid_lib

from src.entities.family import FamilyModel, FamilyMovementModel, RTModel
from src.entities.resident import ResidentModel
from src.family.schemas import FamilyCreate, FamilyUpdate, FamilyFilter, FamilyMovementCreate


# ==================== Family Services ====================

def get_families(db: Session, filters: FamilyFilter) -> Tuple[int, List[FamilyModel]]:
    """Get list of families with filters and pagination"""
    query = db.query(FamilyModel).options(
        joinedload(FamilyModel.rt_rel),
        joinedload(FamilyModel.residents_rel)
    )
    
    # Apply filters
    if filters.rt_id:
        query = query.filter(FamilyModel.rt_id == filters.rt_id)
    
    if filters.status:
        query = query.filter(FamilyModel.status == filters.status)
    
    if filters.family_name:
        query = query.filter(FamilyModel.family_name.ilike(f"%{filters.family_name}%"))
    
    total = query.count()
    results = query.order_by(FamilyModel.family_name).offset(filters.offset).limit(filters.limit).all()
    
    return total, results


def get_family_by_id(db: Session, family_id: UUID) -> Optional[FamilyModel]:
    """Get family by ID with all relationships"""
    family = db.query(FamilyModel).options(
        joinedload(FamilyModel.rt_rel),
        joinedload(FamilyModel.residents_rel),
        joinedload(FamilyModel.homes_rel),
        joinedload(FamilyModel.movements_rel)
    ).filter(FamilyModel.family_id == family_id).first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    return family


def create_family(db: Session, data: FamilyCreate) -> FamilyModel:
    """Create new family"""
    
    # Validate RT exists
    rt = db.query(RTModel).filter(RTModel.rt_id == data.rt_id).first()
    if not rt:
        raise HTTPException(status_code=404, detail="RT not found")
    
    # Validate resident (head of family) if provided
    if data.resident_id:
        resident = db.query(ResidentModel).filter(ResidentModel.resident_id == data.resident_id).first()
        if not resident:
            raise HTTPException(status_code=404, detail="Resident not found")
        
        # Check if resident is already head of another family
        existing_family = db.query(FamilyModel).filter(
            FamilyModel.resident_id == data.resident_id,
            FamilyModel.status == "active"
        ).first()
        if existing_family:
            raise HTTPException(status_code=400, detail="Resident is already head of another active family")
    
    # Create family
    family = FamilyModel(
        family_name=data.family_name,
        kk_path=data.kk_path,
        status=data.status,
        resident_id=data.resident_id,
        rt_id=data.rt_id
    )
    
    db.add(family)
    db.commit()
    db.refresh(family)
    
    return family


def update_family(db: Session, family_id: UUID, data: FamilyUpdate) -> FamilyModel:
    """Update family"""
    family = db.query(FamilyModel).filter(FamilyModel.family_id == family_id).first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Validate RT if changed
    if data.rt_id and data.rt_id != family.rt_id:
        rt = db.query(RTModel).filter(RTModel.rt_id == data.rt_id).first()
        if not rt:
            raise HTTPException(status_code=404, detail="RT not found")
    
    # Validate resident if changed
    if data.resident_id and data.resident_id != family.resident_id:
        resident = db.query(ResidentModel).filter(ResidentModel.resident_id == data.resident_id).first()
        if not resident:
            raise HTTPException(status_code=404, detail="Resident not found")
        
        # Check if resident is already head of another family
        existing_family = db.query(FamilyModel).filter(
            FamilyModel.resident_id == data.resident_id,
            FamilyModel.status == "active",
            FamilyModel.family_id != family_id
        ).first()
        if existing_family:
            raise HTTPException(status_code=400, detail="Resident is already head of another active family")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(family, field, value)
    
    db.commit()
    db.refresh(family)
    
    return family


def delete_family(db: Session, family_id: UUID) -> None:
    """Delete family (soft delete by setting status to inactive)"""
    family = db.query(FamilyModel).filter(FamilyModel.family_id == family_id).first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Check if there are active residents
    active_residents = db.query(ResidentModel).filter(
        ResidentModel.family_id == family_id,
        ResidentModel.status == "approved"
    ).count()
    
    if active_residents > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete family with {active_residents} active residents. Please move or remove residents first."
        )
    
    # Soft delete
    family.status = "inactive"
    db.commit()


def get_family_residents(db: Session, family_id: UUID) -> List[ResidentModel]:
    """Get all residents in a family"""
    family = db.query(FamilyModel).filter(FamilyModel.family_id == family_id).first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    residents = db.query(ResidentModel).filter(
        ResidentModel.family_id == family_id
    ).order_by(ResidentModel.name).all()
    
    return residents


# ==================== Family Movement Services ====================

def create_family_movement(db: Session, data: FamilyMovementCreate) -> FamilyMovementModel:
    """Create family movement record"""
    
    # Validate family exists
    family = db.query(FamilyModel).filter(FamilyModel.family_id == data.family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    movement = FamilyMovementModel(
        reason=data.reason,
        old_address=data.old_address,
        new_address=data.new_address,
        family_id=data.family_id
    )
    
    db.add(movement)
    db.commit()
    db.refresh(movement)
    
    return movement


def get_family_movements(db: Session, family_id: UUID) -> List[FamilyMovementModel]:
    """Get all movements for a family"""
    family = db.query(FamilyModel).filter(FamilyModel.family_id == family_id).first()
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    movements = db.query(FamilyMovementModel).filter(
        FamilyMovementModel.family_id == family_id
    ).order_by(FamilyMovementModel.family_movement_id.desc()).all()
    
    return movements
