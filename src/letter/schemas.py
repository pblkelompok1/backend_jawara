from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Letter Schemas ====================

class LetterResponse(BaseModel):
    letter_id: str
    letter_name: str
    template_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ==================== Letter Transaction Schemas ====================

class DomisiliData(BaseModel):
    """Data schema for Surat Keterangan Domisili"""
    nama_lengkap: str
    nik: str
    tempat_lahir: str
    tanggal_lahir: str
    jenis_kelamin: str
    agama: str
    pekerjaan: str
    status_kawin: str
    alamat_lengkap: str
    sejak_tanggal: str


class PernyataanUsahaData(BaseModel):
    """Data schema for Surat Keterangan Usaha"""
    nama_lengkap: str
    nik: str
    tempat_lahir: str
    tanggal_lahir: str
    jenis_kelamin: str
    pekerjaan: str
    alamat_lengkap: str
    nama_usaha: str
    jenis_usaha: str
    alamat_usaha: str
    mulai_usaha: str
    tujuan_surat: str = "keperluan administrasi"


class LetterTransactionCreate(BaseModel):
    letter_id: str = Field(..., description="UUID of letter type")
    data: Dict[str, Any] = Field(..., description="JSON data for letter template")


class LetterTransactionUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None


class LetterTransactionFilter(BaseModel):
    user_id: Optional[str] = None
    letter_id: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ApprovalRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    rejection_reason: Optional[str] = None


class LetterTransactionResponse(BaseModel):
    letter_transaction_id: str
    application_date: datetime
    status: str
    data: Optional[Dict[str, Any]]
    letter_result_path: Optional[str]
    rejection_reason: Optional[str]
    user_id: str
    letter_id: str
    letter_name: Optional[str] = None
    applicant_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
