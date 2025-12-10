from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import String
from typing import Optional
from datetime import date

class FinanceTransactionData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    amount: int
    category: str
    transaction_date: Optional[date]
    evidence_path: str

class FinanceFilter(BaseModel):
    name: Optional[str] = None
    transaction_type: Optional[str] = None  # 'income' atau 'expense'
    offset: int = 0
    limit: int = 10

class FeeData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    fee_id: UUID
    fee_name: str
    amount: int
    charge_date: Optional[date]
    description: Optional[str]
    fee_category: str
    automation_mode: Optional[str]
    due_date: Optional[date]

class FeeFilter(BaseModel):
    name: Optional[str] = None
    offset: int = 0
    limit: int = 10

class CreateFinanceTransactionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: int = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    transaction_date: Optional[date] = None
    evidence_path: str = Field(..., min_length=1)
    is_expense: bool = False  # True = pengeluaran (amount * -1), False = pemasukan

# ===== NEW SCHEMAS FOR FEE ENDPOINTS =====

# 1. Summary Fee Family
class FeeSummaryResponse(BaseModel):
    total_unpaid_amount: int
    total_unpaid_count: int

# 2. List FeeTransaction
class FeeTransactionData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    fee_transaction_id: int
    transaction_date: Optional[date]
    fee_id: UUID
    fee_name: str
    fee_category: str
    amount: int
    transaction_method: str
    status: str
    family_id: UUID
    family_name: str
    evidence_path: str | None = None

class FeeTransactionFilter(BaseModel):
    family_id: Optional[UUID] = None
    status: Optional[str] = None  # unpaid, pending, paid
    sort_by: str = Field(default="due_date", pattern="^(charge_date|due_date)$")
    offset: int = 0
    limit: int = 10

# 3. Create Fee
class CreateFeeRequest(BaseModel):
    fee_name: str = Field(..., min_length=1, max_length=255)
    amount: int = Field(..., gt=0)
    charge_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    fee_category: str = Field(..., min_length=1)

# 4. List Families with Fee Transaction
class FamilyFeeTransactionData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    family_id: UUID
    family_name: str
    transaction: Optional[dict] = None  # FeeTransaction details

class FamilyFeeFilter(BaseModel):
    status: Optional[str] = None  # Filter by transaction status
    offset: int = 0
    limit: int = 10

# 5. Update Fee Transaction Status
class UpdateFeeTransactionRequest(BaseModel):
    transaction_method: str = Field(default="cash", pattern="^(cash|qris)$")
    # evidence_file will be handled as UploadFile in controller, not in schema
