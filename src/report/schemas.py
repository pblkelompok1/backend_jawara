from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Report Schemas ====================

class ReportCreate(BaseModel):
    category: str = Field(..., min_length=1)
    report_name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    contact_person: Optional[str] = None
    evidence: Optional[List[str]] = None


class ReportUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1)
    report_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    contact_person: Optional[str] = None
    status: Optional[str] = None
    evidence: Optional[List[str]] = None


class ReportFilter(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ReportResponse(BaseModel):
    report_id: str
    category: str
    report_name: str
    description: str
    contact_person: Optional[str]
    status: str
    evidence: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
