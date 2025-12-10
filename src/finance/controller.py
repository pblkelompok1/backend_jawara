from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query, Path, File, UploadFile, Form
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
import os
from src.finance.schemas import (
    FinanceTransactionData, FinanceFilter, FeeData, FeeFilter, CreateFinanceTransactionRequest,
    FeeSummaryResponse, FeeTransactionData, FeeTransactionFilter, CreateFeeRequest,
    FamilyFeeTransactionData, FamilyFeeFilter
)
from src.finance.service import (
    get_finance_list, get_total_balance, get_fees_list, create_finance_transaction,
    get_fee_summary_by_family, get_fee_transactions_list, create_fee_with_transactions,
    get_families_by_fee
)
from uuid import UUID
from src.entities.finance import FeeModel
from src.entities.family import FamilyModel


router = APIRouter(
    prefix='/finance',
    tags=['Finance Service'],
)


@router.get("/list", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=70, seconds=60))])
async def list_finance_transactions(
    filters: FinanceFilter = Depends(),
    db: Session = Depends(get_db)
):
    total, results = get_finance_list(db=db, filters=filters, offset=filters.offset, limit=filters.limit)

    data = [
        FinanceTransactionData(
            name=r['name'],
            amount=r['amount'],
            category=r['category'],
            transaction_date=r['transaction_date'],
            evidence_path=r['evidence_path']
        )
        for r in results
    ]

    return {
        "total": total,
        "limit": filters.limit,
        "offset": filters.offset,
        "data": data
    }   


@router.get("/balance", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=50, seconds=60))])
async def get_balance(
    period: str = Query('all', regex="^(day|month|year|all)$"),
    db: Session = Depends(get_db)
):
    """
    Get total balance dengan filter waktu.
    
    Args:
        period: Filter waktu - 'day' (hari ini), 'month' (bulan ini), 'year' (tahun ini), 'all' (semua waktu)
    
    Returns:
        total_balance: Total saldo (pemasukan - pengeluaran)
        total_income: Total pemasukan (finance + fee paid)
        total_expense: Total pengeluaran
        period: Period yang dipilih
        period_details: Detail breakdown per sumber
    """
    try:
        result = get_total_balance(db=db, period=period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating balance: {str(e)}")


@router.get("/fees", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=70, seconds=60))])
async def list_fees(
    filters: FeeFilter = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get daftar fee (iuran) dengan pagination dan filter.
    
    Args:
        name: Filter berdasarkan nama fee (optional)
        offset: Pagination offset (default: 0)
        limit: Pagination limit (default: 10)
    
    Returns:
        total: Total jumlah fee
        limit: Limit per page
        offset: Offset pagination
        data: List of FeeData
    """
    try:
        total, results = get_fees_list(db=db, filters=filters, offset=filters.offset, limit=filters.limit)
        
        data = [
            FeeData(
                fee_id=fee.fee_id,
                fee_name=fee.fee_name,
                amount=fee.amount,
                charge_date=fee.charge_date,
                description=fee.description,
                fee_category=fee.fee_category,
                automation_mode=fee.automation_mode,
                due_date=fee.due_date
            )
            for fee in results
        ]
        
        return {
            "total": total,
            "limit": filters.limit,
            "offset": filters.offset,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fees: {str(e)}")


@router.post("/transactions", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(SafeRateLimiter(times=30, seconds=60))])
async def create_finance_transaction_endpoint(
    name: str = Form(...),
    amount: int = Form(..., gt=0),
    category: str = Form(...),
    transaction_date: str = Form(None),
    is_expense: bool = Form(False),
    evidence_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Create finance transaction baru (pemasukan atau pengeluaran).
    
    Args:
        name: Nama transaksi
        amount: Jumlah nominal (selalu positif)
        category: Kategori transaksi
        transaction_date: Tanggal transaksi (optional, format: YYYY-MM-DD)
        is_expense: True untuk pengeluaran (amount * -1), False untuk pemasukan
        evidence_file: File bukti transaksi (gambar/PDF, max 50MB)
    
    Returns:
        detail: Success message
        data: Created finance transaction data
    """
    try:
        # Validate file
        if not evidence_file.filename:
            raise HTTPException(status_code=400, detail="Evidence file is required")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_ext = os.path.splitext(evidence_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        file_content = await evidence_file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Reset file pointer
        await evidence_file.seek(0)
        
        new_transaction = await create_finance_transaction(
            db=db,
            name=name,
            amount=amount,
            category=category,
            transaction_date=transaction_date,
            is_expense=is_expense,
            evidence_file=evidence_file
        )
        
        return {
            "detail": "Finance transaction created successfully",
            "data": FinanceTransactionData(
                name=new_transaction.name,
                amount=new_transaction.amount,
                category=new_transaction.category,
                transaction_date=new_transaction.transaction_date,
                evidence_path=new_transaction.evidence_path
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating finance transaction: {str(e)}")


# ===== NEW FEE ENDPOINTS =====

@router.get("/fee-summary/{family_id}", response_model=FeeSummaryResponse, dependencies=[Depends(SafeRateLimiter(times=50, seconds=60))])
async def get_family_fee_summary(
    family_id: UUID = Path(..., description="UUID keluarga"),
    db: Session = Depends(get_db)
):
    """
    Get summary tunggakan fee untuk keluarga tertentu.
    
    Menghitung total amount dan count fee dengan:
    - status = unpaid
    - due_date < today (lewat jatuh tempo)
    
    Args:
        family_id: UUID keluarga
    
    Returns:
        total_unpaid_amount: Total nominal tunggakan
        total_unpaid_count: Jumlah tunggakan
    """
    try:
        result = get_fee_summary_by_family(db=db, family_id=str(family_id))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fee summary: {str(e)}")


@router.get("/fee-transactions", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=70, seconds=60))])
async def list_fee_transactions(
    filters: FeeTransactionFilter = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get list fee transactions dengan filter dan pagination.
    
    Untuk warga keluarga melihat daftar fee yang belum/sudah dibayar.
    
    Args:
        family_id: Filter berdasarkan keluarga (optional)
        status: Filter berdasarkan status (unpaid/pending/paid, optional)
        sort_by: Urutan berdasarkan 'charge_date' atau 'due_date' (default: due_date)
        offset: Pagination offset (default: 0)
        limit: Pagination limit (default: 10)
    
    Returns:
        total: Total jumlah transaksi
        limit: Limit per page
        offset: Offset pagination
        data: List of FeeTransactionData (fee_id, fee_name, amount, status, dll)
    """
    try:
        total, results = get_fee_transactions_list(db=db, filters=filters, offset=filters.offset, limit=filters.limit)
        
        return {
            "total": total,
            "limit": filters.limit,
            "offset": filters.offset,
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fee transactions: {str(e)}")


@router.post("/fees", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(SafeRateLimiter(times=20, seconds=60))])
async def create_fee_endpoint(
    fee: CreateFeeRequest,
    db: Session = Depends(get_db)
):
    """
    Create fee baru dan otomatis membuat transaksi untuk semua keluarga.
    
    Setelah fee dibuat, sistem akan otomatis membuat FeeTransaction untuk:
    - Semua keluarga yang ada
    - Status: unpaid
    - Transaction date: null (belum bayar)
    - Transaction method: cash (default)
    - Evidence path: kosong
    - Automation mode: off (fixed)
    
    Args:
        fee_name: Nama fee
        amount: Nominal fee
        charge_date: Tanggal ditagihkan (optional, default: hari ini)
        due_date: Tanggal jatuh tempo (required)
        description: Deskripsi fee (optional)
        fee_category: Kategori fee
    
    Returns:
        detail: Success message
        fee: Created fee data
        transactions_created: Jumlah transaksi yang dibuat
    """
    try:
        new_fee, transaction_count = create_fee_with_transactions(db=db, fee_data=fee)
        
        return {
            "detail": "Fee created successfully with transactions for all families",
            "fee": FeeData(
                fee_id=new_fee.fee_id,
                fee_name=new_fee.fee_name,
                amount=new_fee.amount,
                charge_date=new_fee.charge_date,
                description=new_fee.description,
                fee_category=new_fee.fee_category,
                automation_mode=new_fee.automation_mode,
                due_date=new_fee.due_date
            ),
            "transactions_created": transaction_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating fee: {str(e)}")


@router.get("/fees/{fee_id}/families", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=70, seconds=60))])
async def list_families_by_fee(
    fee_id: UUID = Path(..., description="UUID fee"),
    filters: FamilyFeeFilter = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get list keluarga dengan transaksi fee tertentu.
    
    Menampilkan keluarga yang memiliki transaksi untuk fee spesifik,
    beserta detail transaksinya.
    
    Args:
        fee_id: UUID fee
        status: Filter berdasarkan status transaksi (optional)
        offset: Pagination offset (default: 0)
        limit: Pagination limit (default: 10)
    
    Returns:
        fee: Data fee
        total: Total jumlah keluarga
        limit: Limit per page
        offset: Offset pagination
        families: List keluarga dengan detail transaksi
    """
    try:
        fee_data, total, families = get_families_by_fee(
            db=db, 
            fee_id=str(fee_id), 
            filters=filters, 
            offset=filters.offset, 
            limit=filters.limit
        )
        
        return {
            "fee": fee_data,
            "total": total,
            "limit": filters.limit,
            "offset": filters.offset,
            "families": families
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching families by fee: {str(e)}")


@router.put("/fee-transactions/{fee_transaction_id}", response_model=dict, dependencies=[Depends(SafeRateLimiter(times=30, seconds=60))])
async def update_fee_transaction_status(
    fee_transaction_id: int = Path(..., description="ID transaksi fee"),
    transaction_method: str = Form("cash", regex="^(cash|qris)$"),
    evidence_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Update status fee transaction menjadi pending (menunggu verifikasi admin).
    
    Endpoint ini digunakan oleh warga keluarga untuk mengirimkan bukti pembayaran fee.
    Status akan berubah dari 'unpaid' ke 'pending', dan admin akan memverifikasi
    untuk mengubah status ke 'paid'.
    
    Args:
        fee_transaction_id: ID transaksi fee yang akan diupdate
        transaction_method: Metode pembayaran ('cash' atau 'qris')
        evidence_file: File bukti pembayaran (gambar/PDF, max 50MB)
    
    Returns:
        detail: Success message
        data: Updated fee transaction data
    
    Restrictions:
        - Hanya transaksi dengan status 'unpaid' yang bisa diupdate
        - Evidence file wajib disertakan
        - Transaction date otomatis diset ke hari ini
    """
    try:
        # Validate file
        if not evidence_file.filename:
            raise HTTPException(status_code=400, detail="Evidence file is required")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_ext = os.path.splitext(evidence_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        file_content = await evidence_file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Reset file pointer
        await evidence_file.seek(0)
        
        # Import service function and entities
        from src.finance.service import update_fee_transaction_to_pending
        from src.entities.finance import FeeModel
        from src.entities.family import FamilyModel
        
        updated_transaction = await update_fee_transaction_to_pending(
            db=db,
            fee_transaction_id=fee_transaction_id,
            transaction_method=transaction_method,
            evidence_file=evidence_file
        )
        
        # Get related data for response
        fee = db.query(FeeModel).filter(FeeModel.fee_id == updated_transaction.fee_id).first()
        family = db.query(FamilyModel).filter(FamilyModel.family_id == updated_transaction.family_id).first()
        
        return {
            "detail": "Fee transaction status updated to pending successfully",
            "data": FeeTransactionData(
                fee_transaction_id=updated_transaction.fee_transaction_id,
                transaction_date=updated_transaction.transaction_date,
                fee_id=updated_transaction.fee_id,
                fee_name=fee.fee_name if fee else "Unknown",
                fee_category=fee.fee_category if fee else "Unknown",
                amount=updated_transaction.amount,
                transaction_method=updated_transaction.transaction_method,
                status=updated_transaction.status,
                family_id=updated_transaction.family_id,
                family_name=family.family_name if family else "Unknown",
                evidence_path=updated_transaction.evidence_path
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating fee transaction: {str(e)}")
