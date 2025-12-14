# Pydantic schemas for Activity CRUD and filter
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID as UUIDType
from datetime import datetime

class ActivityBase(BaseModel):
	activity_name: str
	description: Optional[str] = None
	start_date: datetime
	end_date: Optional[datetime] = None
	location: str
	organizer: str
	status: Optional[str] = None
	banner_img: Optional[str] = None
	preview_images: Optional[List[str]] = None
	category: Optional[str] = None

class ActivityCreate(ActivityBase):
	pass

class ActivityUpdate(BaseModel):
	activity_name: Optional[str] = None
	description: Optional[str] = None
	start_date: Optional[datetime] = None
	end_date: Optional[datetime] = None
	location: Optional[str] = None
	organizer: Optional[str] = None
	status: Optional[str] = None
	banner_img: Optional[str] = None
	preview_images: Optional[List[str]] = None
	category: Optional[str] = None

class ActivityOut(ActivityBase):
	activity_id: UUIDType

	class Config:
		orm_mode = True

class ActivityFilter(BaseModel):
	name: Optional[str] = Field(None, description="Filter by activity_name (LIKE)")
	status: Optional[str] = Field(None, description="Filter by status (LIKE)")
	offset: int = 0
	limit: int = 10

class ActivityListResponse(BaseModel):
	total_count: int
	data: List[ActivityOut]
