# Activity CRUD Service
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.entities.activity import ActivityModel
from src.activity.schemas import ActivityCreate, ActivityUpdate, ActivityFilter
from uuid import UUID

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
	return total_count, results

def get_activity_by_id(db: Session, activity_id: UUID) -> Optional[ActivityModel]:
	return db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()

def create_activity(db: Session, data: ActivityCreate) -> ActivityModel:
	obj = ActivityModel(**data.dict())
	db.add(obj)
	db.commit()
	db.refresh(obj)
	return obj

def update_activity(db: Session, activity_id: UUID, data: ActivityUpdate) -> Optional[ActivityModel]:
	obj = db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()
	if not obj:
		return None
	for field, value in data.dict(exclude_unset=True).items():
		setattr(obj, field, value)
	db.commit()
	db.refresh(obj)
	return obj

def delete_activity(db: Session, activity_id: UUID) -> bool:
	obj = db.query(ActivityModel).filter(ActivityModel.activity_id == activity_id).first()
	if not obj:
		return False
	db.delete(obj)
	db.commit()
	return True
