from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlalchemy import String
from typing import Optional
from datetime import date

class FinanceTransactionData(BaseModel):
    name: str
    amount: int
    category: str
    transaction_date: Optional[date]
    evidence_path: str
    
    class Config:
        orm_mode = True

class FinanceFilter(BaseModel):
    name: Optional[str] = None
    transaction_type: Optional[str] = None  # 'income' atau 'expense'
    offset: int = 0
    limit: int = 10
    
    class Config:
        orm_mode = True

class FeeData(BaseModel):
    fee_id: UUID
    fee_name: str
    amount: int
    charge_date: Optional[date]
    description: Optional[str]
    fee_category: str
    automation_mode: Optional[str]
    
    class Config:
        orm_mode = True

class FeeFilter(BaseModel):
    name: Optional[str] = None
    offset: int = 0
    limit: int = 10
    
    class Config:
        orm_mode = True  
