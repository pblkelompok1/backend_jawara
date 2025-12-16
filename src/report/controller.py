from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.report.schemas import (
    ReportCreate, ReportUpdate, ReportResponse, ReportFilter
)
from src.report.service import (
    create_report, get_reports, get_report_by_id,
    update_report, delete_report, update_report_status,
    save_report_evidence, add_report_evidence
)

router = APIRouter(prefix="/reports", tags=["Reports"])


# ==================== Report Endpoints ====================

@router.post("", response_model=ReportResponse, status_code=201)
async def create_report_endpoint(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """Create a new report"""
    report = create_report(db, report_data)
    
    return ReportResponse(
        report_id=str(report.report_id),
        category=report.category,
        report_name=report.report_name,
        description=report.description,
        contact_person=report.contact_person,
        status=report.status,
        evidence=report.evidence,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.get("", response_model=dict)
async def get_reports_endpoint(
    filters: ReportFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get list of reports with filters and pagination"""
    total, reports = get_reports(db, filters)
    
    data = [
        ReportResponse(
            report_id=str(report.report_id),
            category=report.category,
            report_name=report.report_name,
            description=report.description,
            contact_person=report.contact_person,
            status=report.status,
            evidence=report.evidence,
            created_at=report.created_at,
            updated_at=report.updated_at
        )
        for report in reports
    ]
    
    return {"total": total, "data": data}


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report_endpoint(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Get report by ID"""
    report = get_report_by_id(db, report_id)
    
    return ReportResponse(
        report_id=str(report.report_id),
        category=report.category,
        report_name=report.report_name,
        description=report.description,
        contact_person=report.contact_person,
        status=report.status,
        evidence=report.evidence,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report_endpoint(
    report_id: str,
    report_data: ReportUpdate,
    db: Session = Depends(get_db)
):
    """Update report"""
    report = update_report(db, report_id, report_data)
    
    return ReportResponse(
        report_id=str(report.report_id),
        category=report.category,
        report_name=report.report_name,
        description=report.description,
        contact_person=report.contact_person,
        status=report.status,
        evidence=report.evidence,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.patch("/{report_id}/status", response_model=ReportResponse)
async def update_report_status_endpoint(
    report_id: str,
    status: str = Query(..., description="Status: unsolved, inprogress, solved"),
    db: Session = Depends(get_db)
):
    """Update report status only"""
    report = update_report_status(db, report_id, status)
    
    return ReportResponse(
        report_id=str(report.report_id),
        category=report.category,
        report_name=report.report_name,
        description=report.description,
        contact_person=report.contact_person,
        status=report.status,
        evidence=report.evidence,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.post("/{report_id}/evidence", response_model=ReportResponse)
async def upload_report_evidence_endpoint(
    report_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload evidence files for report (images and PDF allowed)"""
    evidence_paths = []
    for file in files:
        path = await save_report_evidence(file, report_id)
        evidence_paths.append(path)
    
    report = add_report_evidence(db, report_id, evidence_paths)
    
    return ReportResponse(
        report_id=str(report.report_id),
        category=report.category,
        report_name=report.report_name,
        description=report.description,
        contact_person=report.contact_person,
        status=report.status,
        evidence=report.evidence,
        created_at=report.created_at,
        updated_at=report.updated_at
    )


@router.delete("/{report_id}", status_code=204)
async def delete_report_endpoint(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Delete report"""
    delete_report(db, report_id)
    return None
