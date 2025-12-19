from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, UploadFile
from src.entities.report import ReportModel
from src.report.schemas import ReportCreate, ReportUpdate, ReportFilter
import uuid as uuid_lib
from datetime import datetime
from pathlib import Path
import os


# ==================== File Upload Helper ====================

async def save_report_evidence(file: UploadFile, report_id: str) -> str:
    """Save report evidence file and return storage path"""
    storage_dir = Path("storage/report/evidence")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{report_id}_{uuid_lib.uuid4()}{file_extension}"
    file_path = storage_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return str(file_path).replace("\\", "/")


# ==================== Report Services ====================

def create_report(db: Session, report_data: ReportCreate) -> ReportModel:
    """Create a new report"""
    report = ReportModel(
        category=report_data.category,
        report_name=report_data.report_name,
        description=report_data.description,
        contact_person=report_data.contact_person,
        evidence=report_data.evidence or []
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_reports(db: Session, filters: ReportFilter) -> Tuple[int, List[ReportModel]]:
    """Get list of reports with filters and pagination"""
    query = db.query(ReportModel)
    
    # Apply filters
    if filters.category:
        query = query.filter(ReportModel.category == filters.category)
    
    if filters.status:
        query = query.filter(ReportModel.status == filters.status)
    
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                ReportModel.report_name.ilike(search_term),
                ReportModel.description.ilike(search_term),
                ReportModel.contact_person.ilike(search_term)
            )
        )
    
    total = query.count()
    results = query.order_by(ReportModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results


def get_report_by_id(db: Session, report_id: str) -> ReportModel:
    """Get report by ID"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


def update_report(db: Session, report_id: str, report_data: ReportUpdate) -> ReportModel:
    """Update report"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = report_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(report, key, value)
    
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    return report


def delete_report(db: Session, report_id: str) -> None:
    """Delete report"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()


def update_report_status(db: Session, report_id: str, status: str) -> ReportModel:
    """Update report status only"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    valid_statuses = ["unsolved", "inprogress", "solved"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    report.status = status
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    return report


def add_report_evidence(db: Session, report_id: str, evidence_paths: List[str]) -> ReportModel:
    """Add evidence files to report"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_evidence = report.evidence or []
    report.evidence = current_evidence + evidence_paths
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    return report


def add_report_evidence(db: Session, report_id: str, evidence_paths: List[str]) -> ReportModel:
    """Add evidence files to report"""
    report = db.query(ReportModel).filter(
        ReportModel.report_id == uuid_lib.UUID(report_id)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_evidence = report.evidence or []
    report.evidence = current_evidence + evidence_paths
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    return report
