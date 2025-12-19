from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== Family Schemas ====================

class FamilyCreate(BaseModel):
    family_name: str = Field(..., min_length=1, max_length=255)
    kk_path: str = Field(..., min_length=1)
    status: str = Field(default="active")
    resident_id: Optional[UUID] = None  # Kepala keluarga
    rt_id: int

    class Config:
        from_attributes = True


class FamilyUpdate(BaseModel):
    family_name: Optional[str] = Field(None, min_length=1, max_length=255)
    kk_path: Optional[str] = None
    status: Optional[str] = None
    resident_id: Optional[UUID] = None
    rt_id: Optional[int] = None

    class Config:
        from_attributes = True


class FamilyOut(BaseModel):
    family_id: str
    family_name: str
    kk_path: str
    status: str
    resident_id: Optional[str] = None
    rt_id: int
    
    # Related data
    rt_name: Optional[str] = None
    head_of_family_name: Optional[str] = None
    total_members: Optional[int] = None

    class Config:
        from_attributes = True


class FamilyFilter(BaseModel):
    rt_id: Optional[int] = None
    status: Optional[str] = None
    family_name: Optional[str] = None
    offset: int = 0
    limit: int = 10


class FamilyListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[FamilyOut]


# ==================== Family Movement Schemas ====================

class FamilyMovementCreate(BaseModel):
    reason: str = Field(..., min_length=1)
    old_address: str = Field(..., min_length=1)
    new_address: str = Field(..., min_length=1)
    family_id: UUID

    class Config:
        from_attributes = True


class FamilyMovementOut(BaseModel):
    family_movement_id: int
    reason: str
    old_address: str
    new_address: str
    family_id: str

    class Config:
        from_attributes = True
