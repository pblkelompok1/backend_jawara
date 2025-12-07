from datetime import timedelta, datetime, timezone
import secrets
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from fastapi import Depends
from passlib.context import CryptContext
from src.exceptions import AppException
from src.entities.finance import FinanceTransactionModel, FeeTransactionModel
from src.entities.family import FamilyModel
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_

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
        fee_amount = fee_tx.fee_rel.amount if fee_tx.fee_rel else 0
        
        all_transactions.append({
            'name': family_name,
            'amount': fee_amount,
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
