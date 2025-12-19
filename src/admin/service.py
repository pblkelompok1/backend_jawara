from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from typing import Tuple

from src.entities.user import UserModel
from src.entities.resident import ResidentModel
from src.entities.report import ReportModel
from src.entities.letter import LetterTransactionModel
from src.entities.finance import FeeTransactionModel


# ==================== Admin Statistics Services ====================

def get_total_residents(db: Session) -> int:
    """
    Get total number of approved residents/citizens in the system.
    Counts users with role='citizen' and status='approved'
    """
    count = db.query(func.count(UserModel.user_id)).filter(
        and_(
            UserModel.role == 'citizen',
            UserModel.status == 'approved'
        )
    ).scalar()
    
    return count or 0


def get_active_users(db: Session) -> int:
    """
    Get number of active users (logged in within last 30 days).
    Note: Requires last_login field in UserModel. 
    If not available, returns same as total_residents for now.
    """
    # Check if last_login field exists in UserModel
    # For now, return same as total approved users
    # TODO: Add last_login tracking in UserModel and update this query
    
    # When last_login is implemented:
    # thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    # count = db.query(func.count(UserModel.user_id)).filter(
    #     and_(
    #         UserModel.role == 'citizen',
    #         UserModel.status == 'approved',
    #         UserModel.last_login >= thirty_days_ago
    #     )
    # ).scalar()
    
    # Temporary: return total approved users
    return get_total_residents(db)


def get_pending_registrations(db: Session) -> int:
    """
    Get number of pending user registrations waiting for admin approval.
    Counts users with role='citizen' and status='pending'
    """
    count = db.query(func.count(UserModel.user_id)).filter(
        and_(
            UserModel.role == 'citizen',
            UserModel.status == 'pending'
        )
    ).scalar()
    
    return count or 0


def get_new_reports_today(db: Session) -> int:
    """
    Get number of reports submitted today.
    Filters reports where created_at date equals today's date (UTC).
    """
    today = date.today()
    
    count = db.query(func.count(ReportModel.report_id)).filter(
        func.date(ReportModel.created_at) == today
    ).scalar()
    
    return count or 0


def get_pending_letters(db: Session) -> int:
    """
    Get number of letter requests waiting to be processed.
    Counts letter transactions with status='pending'
    """
    count = db.query(func.count(LetterTransactionModel.letter_transaction_id)).filter(
        LetterTransactionModel.status == 'pending'
    ).scalar()
    
    return count or 0


def get_admin_statistics(db: Session) -> dict:
    """
    Get all admin dashboard statistics in one call.
    Returns dictionary with all statistics data.
    """
    return {
        "totalResidents": get_total_residents(db),
        "activeUsers": get_active_users(db),
        "pendingRegistrations": get_pending_registrations(db),
        "newReportsToday": get_new_reports_today(db),
        "pendingLetters": get_pending_letters(db)
    }


# ==================== Finance Summary Services ====================

def get_total_income(db: Session) -> float:
    """
    Get total income from all paid fee transactions.
    Sums amount from fee_transactions where status='paid'
    """
    total = db.query(func.sum(FeeTransactionModel.amount)).filter(
        FeeTransactionModel.status == 'paid'
    ).scalar()
    
    return float(total) if total else 0.0


def get_total_expense(db: Session) -> float:
    """
    Get total expenses.
    Note: Current database only tracks income (fee_transactions).
    If you have separate expense tracking, implement here.
    For now, returns 0.
    """
    # TODO: Implement expense tracking if separate table exists
    # If using same table with type field:
    # total = db.query(func.sum(FinanceModel.amount)).filter(
    #     FinanceModel.type.in_(['expense', 'debit'])
    # ).scalar()
    
    return 0.0


def get_transaction_count(db: Session) -> int:
    """
    Get total number of all financial transactions.
    Counts all fee_transactions regardless of status.
    """
    count = db.query(func.count(FeeTransactionModel.fee_transaction_id)).scalar()
    
    return count or 0


def get_finance_summary(db: Session) -> dict:
    """
    Get finance summary for admin dashboard.
    Returns dictionary with income, expense, balance, and transaction count.
    """
    total_income = get_total_income(db)
    total_expense = get_total_expense(db)
    balance = total_income - total_expense
    
    return {
        "totalIncome": total_income,
        "totalExpense": total_expense,
        "balance": balance,
        "transactionCount": get_transaction_count(db)
    }
