from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from uuid import UUID
from datetime import date

from src.entities.home import HomeModel, HomeHistoryModel
from src.entities.family import FamilyModel
from src.home.schemas import HomeCreate, HomeUpdate, HomeFilter, HomeHistoryCreate


# ==================== Home Services ====================

def get_homes(db: Session, filters: HomeFilter) -> Tuple[int, List[HomeModel]]:
    """Get list of homes with filters and pagination"""
    query = db.query(HomeModel).options(
        joinedload(HomeModel.family).joinedload(FamilyModel.rt_rel),
        joinedload(HomeModel.family).joinedload(FamilyModel.residents_rel)
    )
    
    # Apply filters
    if filters.status:
        query = query.filter(HomeModel.status == filters.status)
    
    if filters.home_name:
        query = query.filter(HomeModel.home_name.ilike(f"%{filters.home_name}%"))
    
    if filters.family_id:
        query = query.filter(HomeModel.family_id == filters.family_id)
    
    if filters.rt_id:
        query = query.join(FamilyModel).filter(FamilyModel.rt_id == filters.rt_id)
    
    total = query.count()
    results = query.order_by(HomeModel.home_name).offset(filters.offset).limit(filters.limit).all()
    
    return total, results


def get_home_by_id(db: Session, home_id: int) -> Optional[HomeModel]:
    """Get home by ID with all relationships"""
    home = db.query(HomeModel).options(
        joinedload(HomeModel.family).joinedload(FamilyModel.rt_rel),
        joinedload(HomeModel.family).joinedload(FamilyModel.residents_rel),
        joinedload(HomeModel.histories)
    ).filter(HomeModel.home_id == home_id).first()
    
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    return home


def create_home(db: Session, data: HomeCreate) -> HomeModel:
    """Create new home"""
    
    # Validate family exists
    family = db.query(FamilyModel).filter(FamilyModel.family_id == data.family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Check if family already has an active home
    existing_home = db.query(HomeModel).filter(
        HomeModel.family_id == data.family_id,
        HomeModel.status == "active"
    ).first()
    
    if existing_home:
        raise HTTPException(
            status_code=400, 
            detail="Family already has an active home. Please deactivate the existing home first."
        )
    
    # Create home
    home = HomeModel(
        home_name=data.home_name,
        home_address=data.home_address,
        status=data.status,
        family_id=data.family_id
    )
    
    db.add(home)
    db.commit()
    db.refresh(home)
    
    # Auto-create home history entry
    if data.status == "active":
        history = HomeHistoryModel(
            home_id=home.home_id,
            family_id=data.family_id,
            moved_in_date=date.today()
        )
        db.add(history)
        db.commit()
    
    return home


def update_home(db: Session, home_id: int, data: HomeUpdate) -> HomeModel:
    """Update home"""
    home = db.query(HomeModel).filter(HomeModel.home_id == home_id).first()
    
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    old_family_id = home.family_id
    
    # Validate family if changed
    if data.family_id and data.family_id != home.family_id:
        family = db.query(FamilyModel).filter(FamilyModel.family_id == data.family_id).first()
        if not family:
            raise HTTPException(status_code=404, detail="Family not found")
        
        # Check if new family already has an active home
        existing_home = db.query(HomeModel).filter(
            HomeModel.family_id == data.family_id,
            HomeModel.status == "active",
            HomeModel.home_id != home_id
        ).first()
        
        if existing_home:
            raise HTTPException(
                status_code=400, 
                detail="New family already has an active home"
            )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(home, field, value)
    
    db.commit()
    db.refresh(home)
    
    # Auto-update home history if family changed
    if data.family_id and data.family_id != old_family_id:
        # Close old history
        old_history = db.query(HomeHistoryModel).filter(
            HomeHistoryModel.home_id == home_id,
            HomeHistoryModel.family_id == old_family_id,
            HomeHistoryModel.moved_out_date == None
        ).first()
        
        if old_history:
            old_history.moved_out_date = date.today()
        
        # Create new history
        new_history = HomeHistoryModel(
            home_id=home_id,
            family_id=data.family_id,
            moved_in_date=date.today()
        )
        db.add(new_history)
        db.commit()
    
    return home


def delete_home(db: Session, home_id: int) -> None:
    """Delete home (soft delete by setting status to inactive)"""
    home = db.query(HomeModel).filter(HomeModel.home_id == home_id).first()
    
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    # Soft delete
    home.status = "inactive"
    
    # Close history
    open_history = db.query(HomeHistoryModel).filter(
        HomeHistoryModel.home_id == home_id,
        HomeHistoryModel.moved_out_date == None
    ).first()
    
    if open_history:
        open_history.moved_out_date = date.today()
    
    db.commit()


# ==================== Home History Services ====================

def get_home_history(db: Session, home_id: int) -> List[HomeHistoryModel]:
    """Get all history records for a home"""
    home = db.query(HomeModel).filter(HomeModel.home_id == home_id).first()
    
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    histories = db.query(HomeHistoryModel).options(
        joinedload(HomeHistoryModel.home_rel)
    ).filter(
        HomeHistoryModel.home_id == home_id
    ).order_by(HomeHistoryModel.moved_in_date.desc()).all()
    
    return histories


def create_home_history(db: Session, data: HomeHistoryCreate) -> HomeHistoryModel:
    """Create home history record"""
    
    # Validate home exists
    home = db.query(HomeModel).filter(HomeModel.home_id == data.home_id).first()
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    # Validate family exists
    family = db.query(FamilyModel).filter(FamilyModel.family_id == data.family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    history = HomeHistoryModel(
        home_id=data.home_id,
        family_id=data.family_id,
        moved_in_date=data.moved_in_date,
        moved_out_date=data.moved_out_date
    )
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return history
