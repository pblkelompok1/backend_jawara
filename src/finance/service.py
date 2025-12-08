from datetime import timedelta, datetime, timezone, date as date_type
import secrets
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from fastapi import Depends
from passlib.context import CryptContext
from src.exceptions import AppException
from src.entities.finance import FinanceTransactionModel, FeeTransactionModel, FeeModel
from src.entities.family import FamilyModel
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, func

import os
import hashlib

def get_finance_list(db: Session, filters, offset: int = 0, limit: int = 10):
    """
    Menggabungkan data dari FinanceTransactionModel dan FeeTransactionModel (status=paid)
    Returns: (total_count, list of dict with FinanceTransactionData structure)
    """
    
    # Query FinanceTransactionModel
    finance_query = db.query(
        FinanceTransactionModel.name,
        FinanceTransactionModel.amount,
        FinanceTransactionModel.category,
        FinanceTransactionModel.transaction_date,
        FinanceTransactionModel.evidence_path
    )
    
    # Query FeeTransactionModel dengan status 'paid'
    fee_query = db.query(
        FamilyModel.family_name.label('name'),
        FeeTransactionModel.fee_id,
        FeeTransactionModel.transaction_date,
        FeeTransactionModel.evidence_path
    ).join(
        FamilyModel, FeeTransactionModel.family_id == FamilyModel.family_id
    ).join(
        FeeTransactionModel.fee_rel
    ).filter(
        FeeTransactionModel.status == 'paid'
    ).options(
        joinedload(FeeTransactionModel.fee_rel)
    )
    
    # Get fee transactions with relationships
    fee_transactions = db.query(FeeTransactionModel).filter(
        FeeTransactionModel.status == 'paid'
    ).options(
        joinedload(FeeTransactionModel.fee_rel),
    ).all()
    
    # Get finance transactions
    finance_transactions = db.query(FinanceTransactionModel).all()
    
    # Convert to unified format
    all_transactions = []
    
    # Add finance transactions
    for ft in finance_transactions:
        all_transactions.append({
            'name': ft.name,
            'amount': ft.amount,
            'category': ft.category,
            'transaction_date': ft.transaction_date,
            'evidence_path': ft.evidence_path,
            'type': 'income' if ft.amount > 0 else 'expense'
        })
    
    # Add fee transactions
    for fee_tx in fee_transactions:
        family = db.query(FamilyModel).filter(FamilyModel.family_id == fee_tx.family_id).first()
        family_name = family.family_name if family else 'Unknown'
        fee_name = fee_tx.fee_rel.fee_name if fee_tx.fee_rel else 'Unknown'
        
        all_transactions.append({
            'name': family_name,
            'amount': fee_tx.amount,
            'category': f'iuran: {fee_name}',
            'transaction_date': fee_tx.transaction_date,
            'evidence_path': fee_tx.evidence_path,
            'type': 'income'
        })
    
    # Apply filters
    filtered_transactions = all_transactions
    
    if filters.name:
        filtered_transactions = [
            t for t in filtered_transactions 
            if filters.name.lower() in t['name'].lower()
        ]
    
    if filters.transaction_type:
        filtered_transactions = [
            t for t in filtered_transactions 
            if t['type'] == filters.transaction_type
        ]
    
    # Sort by transaction_date descending (newest first)
    filtered_transactions.sort(
        key=lambda x: x['transaction_date'] if x['transaction_date'] else datetime.min.date(),
        reverse=True
    )
    
    total_count = len(filtered_transactions)
    
    # Apply pagination
    paginated_transactions = filtered_transactions[offset:offset + limit]
    
    return total_count, paginated_transactions


def get_total_balance(db: Session, period: str = 'all'):
    """
    Menghitung total saldo dari semua finance transaction dan fee transaction (paid)
    
    Args:
        db: Database session
        period: Filter waktu - 'day', 'month', 'year', 'all'
    
    Returns:
        dict dengan total_balance, total_income, total_expense
    """
    today = date_type.today()
    
    # Tentukan filter tanggal berdasarkan period
    date_filter = None
    if period == 'day':
        # Hari ini
        date_filter = lambda date_field: date_field == today
    elif period == 'month':
        # Bulan ini
        start_of_month = today.replace(day=1)
        date_filter = lambda date_field: date_field >= start_of_month
    elif period == 'year':
        # Tahun ini
        start_of_year = today.replace(month=1, day=1)
        date_filter = lambda date_field: date_field >= start_of_year
    # 'all' tidak ada filter
    
    # Query finance transactions
    finance_query = db.query(
        func.coalesce(func.sum(FinanceTransactionModel.amount), 0)
    )
    
    if period != 'all':
        if period == 'day':
            finance_query = finance_query.filter(
                FinanceTransactionModel.transaction_date == today
            )
        elif period == 'month':
            start_of_month = today.replace(day=1)
            finance_query = finance_query.filter(
                FinanceTransactionModel.transaction_date >= start_of_month
            )
        elif period == 'year':
            start_of_year = today.replace(month=1, day=1)
            finance_query = finance_query.filter(
                FinanceTransactionModel.transaction_date >= start_of_year
            )
    
    finance_total = finance_query.scalar() or 0
    
    # Query fee transactions (only paid)
    fee_query = db.query(FeeTransactionModel).filter(
        FeeTransactionModel.status == 'paid'
    ).options(
        joinedload(FeeTransactionModel.fee_rel)
    )
    
    if period != 'all':
        if period == 'day':
            fee_query = fee_query.filter(
                FeeTransactionModel.transaction_date == today
            )
        elif period == 'month':
            start_of_month = today.replace(day=1)
            fee_query = fee_query.filter(
                FeeTransactionModel.transaction_date >= start_of_month
            )
        elif period == 'year':
            start_of_year = today.replace(month=1, day=1)
            fee_query = fee_query.filter(
                FeeTransactionModel.transaction_date >= start_of_year
            )
    
    fee_transactions = fee_query.all()
    
    # Hitung total dari fee (semua fee adalah income)
    fee_total = sum(
        fee_tx.amount
        for fee_tx in fee_transactions
    )
    
    # Calculate totals
    # Finance transactions bisa positif (income) atau negatif (expense)
    finance_income = db.query(
        func.coalesce(func.sum(FinanceTransactionModel.amount), 0)
    ).filter(
        FinanceTransactionModel.amount > 0
    )
    
    finance_expense = db.query(
        func.coalesce(func.sum(FinanceTransactionModel.amount), 0)
    ).filter(
        FinanceTransactionModel.amount < 0
    )
    
    if period != 'all':
        if period == 'day':
            finance_income = finance_income.filter(FinanceTransactionModel.transaction_date == today)
            finance_expense = finance_expense.filter(FinanceTransactionModel.transaction_date == today)
        elif period == 'month':
            start_of_month = today.replace(day=1)
            finance_income = finance_income.filter(FinanceTransactionModel.transaction_date >= start_of_month)
            finance_expense = finance_expense.filter(FinanceTransactionModel.transaction_date >= start_of_month)
        elif period == 'year':
            start_of_year = today.replace(month=1, day=1)
            finance_income = finance_income.filter(FinanceTransactionModel.transaction_date >= start_of_year)
            finance_expense = finance_expense.filter(FinanceTransactionModel.transaction_date >= start_of_year)
    
    finance_income_total = finance_income.scalar() or 0
    finance_expense_total = abs(finance_expense.scalar() or 0)  # Absolute value untuk expense
    
    # Total income = finance income + fee income
    total_income = finance_income_total + fee_total
    total_expense = finance_expense_total
    total_balance = total_income - total_expense
    
    return {
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'period': period,
        'period_details': {
            'finance_income': finance_income_total,
            'fee_income': fee_total,
            'finance_expense': finance_expense_total
        }
    }


def get_fees_list(db: Session, filters, offset: int = 0, limit: int = 10):
    """
    Mengambil daftar fee dengan pagination dan filter
    
    Args:
        db: Database session
        filters: FeeFilter object dengan name filter
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        (total_count, list of FeeModel)
    """
    query = db.query(FeeModel)
    
    # Apply filter by name
    if filters.name:
        query = query.filter(
            FeeModel.fee_name.ilike(f"%{filters.name}%")
        )
    
    # Get total count
    total_count = query.count()
    
    # Sort by charge_date descending (newest first), then by fee_name
    results = (
        query
        .order_by(FeeModel.charge_date.desc(), FeeModel.fee_name)
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return total_count, results


def create_finance_transaction(db: Session, transaction_data):
    """
    Membuat finance transaction baru
    
    Args:
        db: Database session
        transaction_data: CreateFinanceTransactionRequest object
    
    Returns:
        Created FinanceTransactionModel
    """
    # Hitung amount final (jika is_expense=True, kalikan -1)
    final_amount = transaction_data.amount * -1 if transaction_data.is_expense else transaction_data.amount
    
    # Create new finance transaction
    new_transaction = FinanceTransactionModel(
        name=transaction_data.name,
        amount=final_amount,
        category=transaction_data.category,
        transaction_date=transaction_data.transaction_date or date_type.today(),
        evidence_path=transaction_data.evidence_path
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction
