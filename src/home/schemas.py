from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID


# ==================== Home Schemas ====================

class HomeCreate(BaseModel):
    home_name: str = Field(..., min_length=1, max_length=255)
    home_address: str = Field(..., min_length=1)
    status: str = Field(default="active")
    family_id: UUID

    class Config:
        from_attributes = True


class HomeUpdate(BaseModel):
    home_name: Optional[str] = Field(None, min_length=1, max_length=255)
    home_address: Optional[str] = None
    status: Optional[str] = None
    family_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class HomeOut(BaseModel):
    home_id: int
    home_name: str
    home_address: str
    status: str
    family_id: str
    
    # Related data
    family_name: Optional[str] = None
    rt_name: Optional[str] = None
    total_residents: Optional[int] = None

    class Config:
        from_attributes = True


class HomeFilter(BaseModel):
    status: Optional[str] = None
    home_name: Optional[str] = None
    family_id: Optional[UUID] = None
    rt_id: Optional[int] = None
    offset: int = 0
    limit: int = 10


class HomeListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[HomeOut]


# ==================== Home History Schemas ====================

class HomeHistoryCreate(BaseModel):
    home_id: int
    family_id: UUID
    moved_in_date: date
    moved_out_date: Optional[date] = None

    class Config:
        from_attributes = True


class HomeHistoryOut(BaseModel):
    home_id: int
    family_id: str
    moved_in_date: str
    moved_out_date: Optional[str] = None
    
    # Related data
    family_name: Optional[str] = None

    class Config:
        from_attributes = True
