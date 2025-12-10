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


async def create_finance_transaction(
    db: Session,
    name: str,
    amount: int,
    category: str,
    transaction_date: str,
    is_expense: bool,
    evidence_file
):
    """
    Membuat finance transaction baru dengan file upload
    
    Args:
        db: Database session
        name: Nama transaksi
        amount: Jumlah nominal
        category: Kategori transaksi
        transaction_date: Tanggal transaksi (string)
        is_expense: True untuk expense, False untuk income
        evidence_file: UploadFile object
    
    Returns:
        Created FinanceTransactionModel
    """
    import uuid
    import shutil
    from datetime import datetime
    
    # Hitung amount final (jika is_expense=True, kalikan -1)
    final_amount = amount * -1 if is_expense else amount
    
    # Parse transaction_date
    parsed_date = None
    if transaction_date:
        try:
            parsed_date = datetime.strptime(transaction_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = date_type.today()
    else:
        parsed_date = date_type.today()
    
    # Save evidence file
    storage_dir = "storage/finance"
    os.makedirs(storage_dir, exist_ok=True)
    
    file_extension = os.path.splitext(evidence_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}_{evidence_file.filename}"
    evidence_path = os.path.join(storage_dir, unique_filename)
    
    try:
        with open(evidence_path, "wb") as buffer:
            shutil.copyfileobj(evidence_file.file, buffer)
    except Exception as e:
        raise Exception(f"Failed to save evidence file: {str(e)}")
    
    # Create new finance transaction
    new_transaction = FinanceTransactionModel(
        name=name,
        amount=final_amount,
        category=category,
        transaction_date=parsed_date,
        evidence_path=evidence_path
    )
    
    try:
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
    except Exception as e:
        # Rollback and remove uploaded file if database error
        db.rollback()
        try:
            os.remove(evidence_path)
        except Exception:
            pass
        raise Exception(f"Failed to create transaction: {str(e)}")
    
    return new_transaction


# ===== NEW SERVICE FUNCTIONS FOR FEE ENDPOINTS =====

def get_fee_summary_by_family(db: Session, family_id: str):
    """
    Mendapatkan summary tunggakan fee untuk keluarga tertentu.
    Hanya menghitung fee dengan status=unpaid dan due_date < today.
    
    Args:
        db: Database session
        family_id: UUID keluarga
    
    Returns:
        dict dengan total_unpaid_amount dan total_unpaid_count
    """
    today = date_type.today()
    
    # Query fee transactions dengan status unpaid dan due_date < today
    query = db.query(FeeTransactionModel).join(
        FeeModel, FeeTransactionModel.fee_id == FeeModel.fee_id
    ).filter(
        FeeTransactionModel.family_id == family_id,
        FeeTransactionModel.status == 'unpaid',
        FeeModel.due_date < today
    )
    
    transactions = query.all()
    
    total_amount = sum(tx.amount for tx in transactions)
    total_count = len(transactions)
    
    return {
        'total_unpaid_amount': total_amount,
        'total_unpaid_count': total_count
    }


def get_fee_transactions_list(db: Session, filters, offset: int = 0, limit: int = 10):
    """
    Mendapatkan list fee transactions dengan filter dan pagination.
    
    Args:
        db: Database session
        filters: FeeTransactionFilter object
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        (total_count, list of FeeTransactionData)
    """
    query = db.query(FeeTransactionModel).join(
        FeeModel, FeeTransactionModel.fee_id == FeeModel.fee_id
    ).join(
        FamilyModel, FeeTransactionModel.family_id == FamilyModel.family_id
    )
    
    # Apply filters
    if filters.family_id:
        query = query.filter(FeeTransactionModel.family_id == filters.family_id)
    
    if filters.status:
        query = query.filter(FeeTransactionModel.status == filters.status)
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    if filters.sort_by == 'charge_date':
        # Sort by charge_date: yang paling terbaru (descending)
        query = query.order_by(FeeModel.charge_date.desc())
    else:  # due_date (default)
        # Sort by due_date: yang paling dekat dengan hari ini (ascending, nulls last)
        query = query.order_by(FeeModel.due_date.asc().nullslast())
    
    # Apply pagination
    results = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    data = []
    for tx in results:
        fee = db.query(FeeModel).filter(FeeModel.fee_id == tx.fee_id).first()
        family = db.query(FamilyModel).filter(FamilyModel.family_id == tx.family_id).first()
        
        data.append({
            'fee_transaction_id': tx.fee_transaction_id,
            'transaction_date': tx.transaction_date,
            'fee_id': tx.fee_id,
            'fee_name': fee.fee_name if fee else 'Unknown',
            'fee_category': fee.fee_category if fee else 'Unknown',
            'amount': tx.amount,
            'transaction_method': tx.transaction_method or 'cash',
            'status': tx.status or 'unpaid',
            'family_id': tx.family_id,
            'family_name': family.family_name if family else 'Unknown',
            'evidence_path': tx.evidence_path or ''
        })
    
    return total_count, data


def create_fee_with_transactions(db: Session, fee_data):
    """
    Membuat fee baru dan otomatis membuat transaksi untuk semua keluarga.
    
    Args:
        db: Database session
        fee_data: CreateFeeRequest object
    
    Returns:
        Created FeeModel with transaction count
    """
    from src.entities.finance import AutomationMode
    
    # Create new fee
    new_fee = FeeModel(
        fee_name=fee_data.fee_name,
        amount=fee_data.amount,
        charge_date=fee_data.charge_date or date_type.today(),
        due_date=fee_data.due_date,
        description=fee_data.description,
        fee_category=fee_data.fee_category,
        automation_mode=AutomationMode.off.value  # Always set to 'off'
    )
    
    db.add(new_fee)
    db.flush()  # Flush to get fee_id
    
    # Get all families
    families = db.query(FamilyModel).all()
    
    # Create fee transaction for each family
    transaction_count = 0
    for family in families:
        fee_transaction = FeeTransactionModel(
            transaction_date=None,  # Belum bayar
            fee_id=new_fee.fee_id,
            amount=new_fee.amount,
            transaction_method='cash',  # Default
            status='unpaid',  # Default
            family_id=family.family_id,
            evidence_path=''  # Kosong karena belum bayar
        )
        db.add(fee_transaction)
        transaction_count += 1
    
    db.commit()
    db.refresh(new_fee)
    
    return new_fee, transaction_count


def get_families_by_fee(db: Session, fee_id: str, filters, offset: int = 0, limit: int = 10):
    """
    Mendapatkan list keluarga dengan transaksi fee tertentu.
    
    Args:
        db: Database session
        fee_id: UUID fee
        filters: FamilyFeeFilter object
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        (fee_data, total_count, list of families with transactions)
    """
    # Get fee data
    fee = db.query(FeeModel).filter(FeeModel.fee_id == fee_id).first()
    if not fee:
        raise AppException("Fee not found")
    
    # Query transactions for this fee
    query = db.query(FeeTransactionModel).filter(
        FeeTransactionModel.fee_id == fee_id
    )
    
    # Apply status filter
    if filters.status:
        query = query.filter(FeeTransactionModel.status == filters.status)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    transactions = query.offset(offset).limit(limit).all()
    
    # Build response
    families_data = []
    for tx in transactions:
        family = db.query(FamilyModel).filter(FamilyModel.family_id == tx.family_id).first()
        
        families_data.append({
            'family_id': tx.family_id,
            'family_name': family.family_name if family else 'Unknown',
            'transaction': {
                'fee_transaction_id': tx.fee_transaction_id,
                'status': tx.status,
                'amount': tx.amount,
                'transaction_date': tx.transaction_date,
                'transaction_method': tx.transaction_method,
                'evidence_path': tx.evidence_path
            }
        })
    
    fee_data = {
        'fee_id': fee.fee_id,
        'fee_name': fee.fee_name,
        'amount': fee.amount,
        'charge_date': fee.charge_date,
        'due_date': fee.due_date,
        'description': fee.description,
        'fee_category': fee.fee_category,
        'automation_mode': fee.automation_mode
    }
    
    return fee_data, total_count, families_data


async def update_fee_transaction_to_pending(
    db: Session,
    fee_transaction_id: int,
    transaction_method: str,
    evidence_file
):
    """
    Update fee transaction status ke pending dengan upload bukti pembayaran.
    
    Args:
        db: Database session
        fee_transaction_id: ID transaksi fee
        transaction_method: Metode pembayaran (cash/qris)
        evidence_file: UploadFile bukti pembayaran
    
    Returns:
        Updated FeeTransactionModel
    """
    import os
    import uuid
    from datetime import date as date_type
    from fastapi import HTTPException
    
    # Get existing transaction
    transaction = db.query(FeeTransactionModel).filter(
        FeeTransactionModel.fee_transaction_id == fee_transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Fee transaction not found")
    
    # Validate status transition (only unpaid -> pending)
    if transaction.status != 'unpaid':
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot update transaction with status '{transaction.status}' to pending. Only 'unpaid' transactions can be updated."
        )
    
    # Save evidence file
    storage_dir = "storage/finance"
    os.makedirs(storage_dir, exist_ok=True)
    
    file_extension = os.path.splitext(evidence_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}_{evidence_file.filename}"
    evidence_path = os.path.join(storage_dir, unique_filename)
    
    try:
        with open(evidence_path, "wb") as f:
            content = await evidence_file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save evidence file: {str(e)}")
    
    # Update transaction
    transaction.status = 'pending'
    transaction.transaction_method = transaction_method
    transaction.evidence_path = evidence_path
    transaction.transaction_date = date_type.today()
    
    try:
        db.commit()
        db.refresh(transaction)
    except Exception as e:
        # Rollback and delete uploaded file if database error
        db.rollback()
        if os.path.exists(evidence_path):
            try:
                os.remove(evidence_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")
    
    return transaction
