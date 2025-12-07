from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from starlette import status
from src.database.core import get_db
from src.rate_limit import SafeRateLimiter
from sqlalchemy.orm import Session
from src.finance.schemas import FinanceTransactionData, FinanceFilter
from src.finance.service import get_finance_list


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
    