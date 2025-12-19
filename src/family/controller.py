from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pathlib import Path
import uuid as uuid_lib

from src.database.core import get_db
from src.family import service
from src.family.schemas import (
    FamilyCreate, FamilyUpdate, FamilyOut, FamilyFilter, FamilyListResponse,
    FamilyMovementCreate, FamilyMovementOut
)

router = APIRouter(prefix="/family", tags=["Family"], redirect_slashes=False)


# ==================== Family CRUD ====================

@router.get("/", response_model=FamilyListResponse)
def list_families(
    rt_id: int = Query(None, description="Filter by RT ID"),
    status: str = Query(None, description="Filter by status"),
    family_name: str = Query(None, description="Filter by family name (LIKE)"),
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get list of families with filters"""
    filters = FamilyFilter(
        rt_id=rt_id,
        status=status,
        family_name=family_name,
        offset=offset,
        limit=limit
    )
    
    total, families = service.get_families(db, filters)
    
    # Transform to response
    data = []
    for family in families:
        family_out = FamilyOut(
            family_id=str(family.family_id),
            family_name=family.family_name,
            kk_path=family.kk_path,
            status=family.status,
            resident_id=str(family.resident_id) if family.resident_id else None,
            rt_id=family.rt_id,
            rt_name=family.rt_rel.rt_name if family.rt_rel else None,
            head_of_family_name=next(
                (r.name for r in family.residents_rel if r.resident_id == family.resident_id),
                None
            ),
            total_members=len(family.residents_rel)
        )
        data.append(family_out)
    
    return FamilyListResponse(total=total, offset=offset, limit=limit, data=data)


@router.get("/{family_id}", response_model=FamilyOut)
def get_family(family_id: UUID, db: Session = Depends(get_db)):
    """Get family by ID"""
    family = service.get_family_by_id(db, family_id)
    
    return FamilyOut(
        family_id=str(family.family_id),
        family_name=family.family_name,
        kk_path=family.kk_path,
        status=family.status,
        resident_id=str(family.resident_id) if family.resident_id else None,
        rt_id=family.rt_id,
        rt_name=family.rt_rel.rt_name if family.rt_rel else None,
        head_of_family_name=next(
            (r.name for r in family.residents_rel if r.resident_id == family.resident_id),
            None
        ),
        total_members=len(family.residents_rel)
    )


@router.post("/", response_model=FamilyOut, status_code=status.HTTP_201_CREATED)
def create_family(data: FamilyCreate, db: Session = Depends(get_db)):
    """Create new family"""
    family = service.create_family(db, data)
    
    return FamilyOut(
        family_id=str(family.family_id),
        family_name=family.family_name,
        kk_path=family.kk_path,
        status=family.status,
        resident_id=str(family.resident_id) if family.resident_id else None,
        rt_id=family.rt_id
    )


@router.put("/{family_id}", response_model=FamilyOut)
def update_family(family_id: UUID, data: FamilyUpdate, db: Session = Depends(get_db)):
    """Update family"""
    family = service.update_family(db, family_id, data)
    
    return FamilyOut(
        family_id=str(family.family_id),
        family_name=family.family_name,
        kk_path=family.kk_path,
        status=family.status,
        resident_id=str(family.resident_id) if family.resident_id else None,
        rt_id=family.rt_id
    )


@router.delete("/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family(family_id: UUID, db: Session = Depends(get_db)):
    """Delete family (soft delete)"""
    service.delete_family(db, family_id)
    return None


# ==================== Family Residents ====================

@router.get("/{family_id}/residents")
def get_family_residents(family_id: UUID, db: Session = Depends(get_db)):
    """Get all residents in a family"""
    residents = service.get_family_residents(db, family_id)
    
    return {
        "total": len(residents),
        "data": [
            {
                "resident_id": str(r.resident_id),
                "nik": r.nik,
                "name": r.name,
                "phone": r.phone,
                "family_role": r.family_role,
                "gender": r.gender,
                "date_of_birth": r.date_of_birth.isoformat() if r.date_of_birth else None,
                "is_deceased": r.is_deceased,
                "status": r.status
            } for r in residents
        ]
    }


# ==================== KK Upload ====================

@router.post("/{family_id}/upload-kk")
async def upload_kk(family_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload Kartu Keluarga (KK) document"""
    
    # Validate family exists
    family = service.get_family_by_id(db, family_id)
    
    # Validate file type
    allowed_extensions = ["pdf", "jpg", "jpeg", "png"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create storage directory
    storage_dir = Path("storage/kk")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    filename = f"{uuid_lib.uuid4()}.{file_ext}"
    filepath = storage_dir / filename
    
    # Save file
    try:
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update family kk_path
    file_path_str = str(filepath).replace("\\", "/")
    family.kk_path = file_path_str
    db.commit()
    
    return {
        "message": "KK uploaded successfully",
        "kk_path": file_path_str
    }


# ==================== Family Movement ====================

@router.post("/{family_id}/movements", response_model=FamilyMovementOut, status_code=status.HTTP_201_CREATED)
def create_movement(family_id: UUID, data: FamilyMovementCreate, db: Session = Depends(get_db)):
    """Record family movement/relocation"""
    data.family_id = family_id
    movement = service.create_family_movement(db, data)
    
    return FamilyMovementOut(
        family_movement_id=movement.family_movement_id,
        reason=movement.reason,
        old_address=movement.old_address,
        new_address=movement.new_address,
        family_id=str(movement.family_id)
    )


@router.get("/{family_id}/movements", response_model=List[FamilyMovementOut])
def get_movements(family_id: UUID, db: Session = Depends(get_db)):
    """Get family movement history"""
    movements = service.get_family_movements(db, family_id)
    
    return [
        FamilyMovementOut(
            family_movement_id=m.family_movement_id,
            reason=m.reason,
            old_address=m.old_address,
            new_address=m.new_address,
            family_id=str(m.family_id)
        ) for m in movements
    ]
