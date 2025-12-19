# FastAPI router for Activity CRUD
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
from pathlib import Path
from src.database.core import get_db
from src.activity import service
from src.activity.schemas import (
	ActivityCreate, ActivityUpdate, ActivityOut, ActivityFilter, ActivityListResponse
)

router = APIRouter(prefix="/activity", tags=["Activity"], redirect_slashes=False)

@router.get("/", response_model=ActivityListResponse)
def list_activities(
	name: str = Query(None, description="Filter by activity_name (LIKE)"),
	status_: str = Query(None, alias="status", description="Filter by status (LIKE)"),
	offset: int = 0,
	limit: int = 10,
	db: Session = Depends(get_db)
):
	filters = ActivityFilter(name=name, status=status_, offset=offset, limit=limit)
	total_count, activities = service.get_activities(db, filters)
	
	data = [
		ActivityOut(
			activity_id=a.activity_id,
			activity_name=a.activity_name,
			description=a.description,
			start_date=a.start_date,
			end_date=a.end_date,
			location=a.location,
			organizer=a.organizer,
			status=a.status,
			banner_img=a.banner_img,
			preview_images=a.preview_images if a.preview_images else [],
			category=a.category
		)
		for a in activities
	]
	
	return ActivityListResponse(
		total_count=total_count,
		data=data
	)

@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: UUID, db: Session = Depends(get_db)):
	obj = service.get_activity_by_id(db, activity_id)
	if not obj:
		raise HTTPException(status_code=404, detail="Activity not found")
	return ActivityOut(
		activity_id=obj.activity_id,
		activity_name=obj.activity_name,
		description=obj.description,
		start_date=obj.start_date,
		end_date=obj.end_date,
		location=obj.location,
		organizer=obj.organizer,
		status=obj.status,
		banner_img=obj.banner_img,
		preview_images=obj.preview_images if obj.preview_images else [],
		category=obj.category
	)

@router.post("/", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(data: ActivityCreate, db: Session = Depends(get_db)):
	obj = service.create_activity(db, data)
	return ActivityOut(
		activity_id=obj.activity_id,
		activity_name=obj.activity_name,
		description=obj.description,
		start_date=obj.start_date,
		end_date=obj.end_date,
		location=obj.location,
		organizer=obj.organizer,
		status=obj.status,
		banner_img=obj.banner_img,
		preview_images=obj.preview_images if obj.preview_images else [],
		category=obj.category
	)

@router.put("/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: UUID, data: ActivityUpdate, db: Session = Depends(get_db)):
	obj = service.update_activity(db, activity_id, data)
	if not obj:
		raise HTTPException(status_code=404, detail="Activity not found")
	return ActivityOut(
		activity_id=obj.activity_id,
		activity_name=obj.activity_name,
		description=obj.description,
		start_date=obj.start_date,
		end_date=obj.end_date,
		location=obj.location,
		organizer=obj.organizer,
		status=obj.status,
		banner_img=obj.banner_img,
		preview_images=obj.preview_images if obj.preview_images else [],
		category=obj.category
	)

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: UUID, db: Session = Depends(get_db)):
	ok = service.delete_activity(db, activity_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Activity not found")
	return None


@router.post("/{activity_id}/upload-images")
async def upload_activity_images(
	activity_id: UUID,
	files: List[UploadFile] = File(...),
	db: Session = Depends(get_db)
):
	"""Upload multiple preview images for an activity (max 10)"""
	
	# Validate activity exists
	activity = service.get_activity_by_id(db, activity_id)
	if not activity:
		raise HTTPException(status_code=404, detail="Activity not found")
	
	# Validate max 10 images
	if len(files) > 10:
		raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
	
	# Validate file types
	allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
	for file in files:
		if file.content_type not in allowed_types:
			raise HTTPException(
				status_code=400, 
				detail=f"Invalid file type for {file.filename}. Only JPEG, PNG, WEBP allowed"
			)
	
	# Save files
	saved_paths = []
	upload_dir = Path("storage/activity")
	upload_dir.mkdir(parents=True, exist_ok=True)
	
	for file in files:
		# Generate unique filename
		ext = file.filename.split(".")[-1].lower()
		filename = f"{uuid4()}.{ext}"
		filepath = upload_dir / filename
		
		# Save file
		with open(filepath, "wb") as f:
			content = await file.read()
			f.write(content)
		
		saved_paths.append(str(filepath).replace("\\", "/"))
	
	# Update activity preview_images (append to existing)
	existing_images = activity.preview_images or []
	activity.preview_images = existing_images + saved_paths
	db.commit()
	
	return {
		"activity_id": str(activity_id),
		"uploaded_images": saved_paths,
		"total_images": len(activity.preview_images)
	}
