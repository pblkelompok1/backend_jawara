from pydantic import BaseModel
from typing import Optional


# ==================== Admin Statistics Schemas ====================

class AdminStatisticsOut(BaseModel):
    """Statistics for admin dashboard summary cards"""
    totalResidents: int
    activeUsers: int
    pendingRegistrations: int
    newReportsToday: int
    pendingLetters: int

    class Config:
        from_attributes = True


class AdminStatisticsResponse(BaseModel):
    """Wrapper response for statistics endpoint"""
    success: bool = True
    data: AdminStatisticsOut


# ==================== Finance Summary Schemas ====================

class FinanceSummaryOut(BaseModel):
    """Finance summary for admin dashboard"""
    totalIncome: float
    totalExpense: float
    balance: float
    transactionCount: int

    class Config:
        from_attributes = True


class FinanceSummaryResponse(BaseModel):
    """Wrapper response for finance summary endpoint"""
    success: bool = True
    data: FinanceSummaryOut


# ==================== Error Response Schema ====================

class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
