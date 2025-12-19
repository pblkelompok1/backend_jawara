from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException
from src.entities.letter import LetterModel, LetterTransactionModel
from src.entities.user import UserModel
from src.entities.resident import ResidentModel
from src.letter.schemas import (
    LetterTransactionCreate, LetterTransactionUpdate, 
    LetterTransactionFilter, ApprovalRequest
)
import uuid as uuid_lib
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import qrcode
from io import BytesIO
import base64
import os


# ==================== QR Code Generator ====================

def generate_dummy_qr_code(text: str) -> str:
    """Generate dummy QR code and return as base64 data URL"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


# ==================== PDF Generator ====================

def generate_letter_pdf(letter_type: str, data: Dict[str, Any], output_path: str) -> str:
    """Generate PDF from HTML template using Jinja2 and WeasyPrint"""
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "template"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Determine template file
    template_map = {
        "Surat Keterangan Domisili": "domisili_new.html",
        "Surat Keterangan Usaha": "pernyataan_usaha_new.html"
    }
    
    template_file = template_map.get(letter_type)
    if not template_file:
        raise HTTPException(status_code=400, detail=f"Template not found for letter type: {letter_type}")
    
    template = env.get_template(template_file)
    
    # Add default data (dummy data for Kelurahan, RT, RW)
    current_date = datetime.now()
    nomor_surat = f"{uuid_lib.uuid4().hex[:8].upper()}/SKT/{current_date.strftime('%m/%Y')}"
    
    template_data = {
        **data,
        "kelurahan": "JAWARA",
        "rt": "001",
        "rw": "003",
        "alamat_kelurahan": "Jl. Contoh No. 123, Kota ABC",
        "tempat": "Kota ABC",
        "tanggal_surat": current_date.strftime("%d %B %Y"),
        "nomor_surat": nomor_surat,
        "nama_rt": "Budi Santoso",
        "nama_lurah": "Dr. Ahmad Yani, S.H.",
        "nip_lurah": "197512312005011001",
        # Generate QR codes
        "qr_code_url": generate_dummy_qr_code(f"RT_SIGNATURE_{nomor_surat}"),
        "qr_code_rt_url": generate_dummy_qr_code(f"RT_SIGNATURE_{nomor_surat}"),
        "qr_code_lurah_url": generate_dummy_qr_code(f"LURAH_SIGNATURE_{nomor_surat}"),
        "qr_code_pemohon_url": generate_dummy_qr_code(f"APPLICANT_{data.get('nik', 'UNKNOWN')}"),
    }
    
    # Render HTML
    html_content = template.render(**template_data)
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate PDF using xhtml2pdf
    try:
        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(
                src=html_content,
                dest=pdf_file,
                encoding='utf-8'
            )
            
            if pisa_status.err:
                raise Exception(f"PDF generation failed with errors")
    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")
    
    return output_path


# ==================== Letter Services ====================

def get_letters(db: Session) -> List[LetterModel]:
    """Get all available letter types"""
    return db.query(LetterModel).order_by(LetterModel.letter_name).all()


def get_letter_by_id(db: Session, letter_id: str) -> LetterModel:
    """Get letter by ID"""
    letter = db.query(LetterModel).filter(
        LetterModel.letter_id == uuid_lib.UUID(letter_id)
    ).first()
    
    if not letter:
        raise HTTPException(status_code=404, detail="Letter type not found")
    
    return letter


# ==================== Letter Transaction Services ====================

def create_letter_transaction(db: Session, user_id: str, transaction_data: LetterTransactionCreate) -> LetterTransactionModel:
    """Create new letter request (citizen request)"""
    
    # Verify letter exists
    letter = get_letter_by_id(db, transaction_data.letter_id)
    
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.user_id == uuid_lib.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create transaction
    transaction = LetterTransactionModel(
        user_id=uuid_lib.UUID(user_id),
        letter_id=uuid_lib.UUID(transaction_data.letter_id),
        data=transaction_data.data,
        status="pending"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


def get_letter_transactions(db: Session, filters: LetterTransactionFilter) -> Tuple[int, List[LetterTransactionModel]]:
    """Get list of letter transactions with filters and pagination"""
    query = db.query(LetterTransactionModel).options(
        joinedload(LetterTransactionModel.letter),
        joinedload(LetterTransactionModel.user).joinedload(UserModel.resident)
    )
    
    # Apply filters
    if filters.user_id:
        query = query.filter(LetterTransactionModel.user_id == uuid_lib.UUID(filters.user_id))
    
    if filters.letter_id:
        query = query.filter(LetterTransactionModel.letter_id == uuid_lib.UUID(filters.letter_id))
    
    if filters.status:
        query = query.filter(LetterTransactionModel.status == filters.status)
    
    total = query.count()
    results = query.order_by(LetterTransactionModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results


def get_transaction_by_id(db: Session, transaction_id: str) -> LetterTransactionModel:
    """Get transaction by ID"""
    transaction = db.query(LetterTransactionModel).options(
        joinedload(LetterTransactionModel.letter),
        joinedload(LetterTransactionModel.user).joinedload(UserModel.resident)
    ).filter(
        LetterTransactionModel.letter_transaction_id == uuid_lib.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Letter transaction not found")
    
    return transaction


def update_transaction_status(db: Session, transaction_id: str, approval: ApprovalRequest) -> LetterTransactionModel:
    """Update transaction status (admin approve/reject)"""
    
    transaction = db.query(LetterTransactionModel).options(
        joinedload(LetterTransactionModel.letter)
    ).filter(
        LetterTransactionModel.letter_transaction_id == uuid_lib.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Letter transaction not found")
    
    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="Transaction already processed")
    
    # If approved, generate PDF first
    if approval.status == "approved":
        try:
            # Generate PDF
            filename = f"{transaction_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            output_path = f"storage/letters/{filename}"
            
            generate_letter_pdf(
                letter_type=transaction.letter.letter_name,
                data=transaction.data,
                output_path=output_path
            )
            
            transaction.letter_result_path = output_path
            transaction.status = "approved"
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
    
    elif approval.status == "rejected":
        transaction.status = "rejected"
        transaction.rejection_reason = approval.rejection_reason
    
    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    
    return transaction


def delete_transaction(db: Session, transaction_id: str) -> None:
    """Delete transaction"""
    transaction = db.query(LetterTransactionModel).filter(
        LetterTransactionModel.letter_transaction_id == uuid_lib.UUID(transaction_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Letter transaction not found")
    
    # Delete PDF file if exists
    if transaction.letter_result_path and os.path.exists(transaction.letter_result_path):
        os.remove(transaction.letter_result_path)
    
    db.delete(transaction)
    db.commit()
