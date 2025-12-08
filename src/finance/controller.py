from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from src.finance.schemas import FinanceTransactionData, FinanceFilter, FeeData, FeeFilter
from src.finance.service import get_finance_list, get_total_balance, get_fees_list


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
                automation_mode=fee.automation_mode
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
    
    