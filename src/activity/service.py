# Activity CRUD Service
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.entities.activity import ActivityModel
from src.activity.schemas import ActivityCreate, ActivityUpdate, ActivityFilter
from uuid import UUID

# Helper function to format status (underscore to space, title case)
def format_status(status: str) -> str:
	"""Convert status from 'akan_datang' to 'Akan Datang'"""
	if not status:
		return status
	return status.replace('_', ' ').title()

def get_activities(db: Session, filters: ActivityFilter) -> Tuple[int, List[ActivityModel]]:
	query_filters = []
	# LIKE filter for name
	if filters.name:
		query_filters.append(ActivityModel.activity_name.ilike(f"%{filters.name}%"))
	# LIKE filter for status
	if filters.status:
		query_filters.append(ActivityModel.status.ilike(f"%{filters.status}%"))

	query = db.query(ActivityModel)
	if query_filters:
		query = query.filter(and_(*query_filters))

	total_count = query.count()
	results = (
		query
		.order_by(ActivityModel.start_date.desc())
		.offset(filters.offset)
		.limit(filters.limit)
		.all()
	)
	# Format status for all results
	for result in results:
		if result.status:
			result.status = format_status(result.status)
		if result.category:
			result.category = format_status(result.category)
	return total_count, results

def get_activity_by_id(db: Session, activity_id: UUID) -> Optional[ActivityModel]:
	result = db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()
	if result:
		if result.status:
			result.status = format_status(result.status)
		if result.category:
			result.category = format_status(result.category)
	return result

def create_activity(db: Session, data: ActivityCreate) -> ActivityModel:
	obj = ActivityModel(**data.dict())
	db.add(obj)
	db.commit()
	db.refresh(obj)
	# Format status for response
	if obj.status:
		obj.status = format_status(obj.status)
	if obj.category:
		obj.category = format_status(obj.category)
	return obj

def update_activity(db: Session, activity_id: UUID, data: ActivityUpdate) -> Optional[ActivityModel]:
	obj = db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()
	if not obj:
		return None
	for field, value in data.dict(exclude_unset=True).items():
		setattr(obj, field, value)
	db.commit()
	db.refresh(obj)
	# Format status for response
	if obj.status:
		obj.status = format_status(obj.status)
	if obj.category:
		obj.category = format_status(obj.category)
	return obj

def delete_activity(db: Session, activity_id: UUID) -> bool:
	obj = db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()
	if not obj:
		return False
	db.delete(obj)
	db.commit()
	return True
