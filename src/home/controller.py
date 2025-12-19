from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.database.core import get_db
from src.home import service
from src.home.schemas import (
    HomeCreate, HomeUpdate, HomeOut, HomeFilter, HomeListResponse,
    HomeHistoryCreate, HomeHistoryOut
)

router = APIRouter(prefix="/home", tags=["Home"], redirect_slashes=False)


# ==================== Home CRUD ====================

@router.get("/", response_model=HomeListResponse)
def list_homes(
    status: str = Query(None, description="Filter by status"),
    home_name: str = Query(None, description="Filter by home name (LIKE)"),
    family_id: UUID = Query(None, description="Filter by family ID"),
    rt_id: int = Query(None, description="Filter by RT ID"),
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get list of homes with filters"""
    filters = HomeFilter(
        status=status,
        home_name=home_name,
        family_id=family_id,
        rt_id=rt_id,
        offset=offset,
        limit=limit
    )
    
    total, homes = service.get_homes(db, filters)
    
    # Transform to response
    data = []
    for home in homes:
        home_out = HomeOut(
            home_id=home.home_id,
            home_name=home.home_name,
            home_address=home.home_address,
            status=home.status,
            family_id=str(home.family_id),
            family_name=home.family.family_name if home.family else None,
            rt_name=home.family.rt_rel.rt_name if home.family and home.family.rt_rel else None,
            total_residents=len(home.family.residents_rel) if home.family else 0
        )
        data.append(home_out)
    
    return HomeListResponse(total=total, offset=offset, limit=limit, data=data)


@router.get("/{home_id}", response_model=HomeOut)
def get_home(home_id: int, db: Session = Depends(get_db)):
    """Get home by ID"""
    home = service.get_home_by_id(db, home_id)
    
    return HomeOut(
        home_id=home.home_id,
        home_name=home.home_name,
        home_address=home.home_address,
        status=home.status,
        family_id=str(home.family_id),
        family_name=home.family.family_name if home.family else None,
        rt_name=home.family.rt_rel.rt_name if home.family and home.family.rt_rel else None,
        total_residents=len(home.family.residents_rel) if home.family else 0
    )


@router.post("/", response_model=HomeOut, status_code=status.HTTP_201_CREATED)
def create_home(data: HomeCreate, db: Session = Depends(get_db)):
    """Create new home"""
    home = service.create_home(db, data)
    
    return HomeOut(
        home_id=home.home_id,
        home_name=home.home_name,
        home_address=home.home_address,
        status=home.status,
        family_id=str(home.family_id)
    )


@router.put("/{home_id}", response_model=HomeOut)
def update_home(home_id: int, data: HomeUpdate, db: Session = Depends(get_db)):
    """Update home"""
    home = service.update_home(db, home_id, data)
    
    return HomeOut(
        home_id=home.home_id,
        home_name=home.home_name,
        home_address=home.home_address,
        status=home.status,
        family_id=str(home.family_id)
    )


@router.delete("/{home_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_home(home_id: int, db: Session = Depends(get_db)):
    """Delete home (soft delete)"""
    service.delete_home(db, home_id)
    return None


# ==================== Home History ====================

@router.get("/{home_id}/history", response_model=List[HomeHistoryOut])
def get_home_history(home_id: int, db: Session = Depends(get_db)):
    """Get home occupancy history"""
    histories = service.get_home_history(db, home_id)
    
    return [
        HomeHistoryOut(
            home_id=h.home_id,
            family_id=str(h.family_id),
            moved_in_date=h.moved_in_date.isoformat() if h.moved_in_date else None,
            moved_out_date=h.moved_out_date.isoformat() if h.moved_out_date else None,
            family_name=None  # Can be enriched if needed
        ) for h in histories
    ]


@router.post("/history", response_model=HomeHistoryOut, status_code=status.HTTP_201_CREATED)
def create_home_history(data: HomeHistoryCreate, db: Session = Depends(get_db)):
    """Create home history record"""
    history = service.create_home_history(db, data)
    
    return HomeHistoryOut(
        home_id=history.home_id,
        family_id=str(history.family_id),
        moved_in_date=history.moved_in_date.isoformat() if history.moved_in_date else None,
        moved_out_date=history.moved_out_date.isoformat() if history.moved_out_date else None
    )
