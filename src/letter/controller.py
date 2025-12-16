from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.letter.schemas import (
    LetterResponse, LetterTransactionCreate, LetterTransactionResponse,
    LetterTransactionFilter, ApprovalRequest
)
from src.letter.service import (
    get_letters, get_letter_by_id,
    create_letter_transaction, get_letter_transactions,
    get_transaction_by_id, update_transaction_status, delete_transaction
)

router = APIRouter(prefix="/letters", tags=["Letters"])


# ==================== Letter Type Endpoints ====================

@router.get("", response_model=list[LetterResponse])
async def get_letter_types_endpoint(db: Session = Depends(get_db)):
    """Get all available letter types"""
    letters = get_letters(db)
    
    return [
        LetterResponse(
            letter_id=str(letter.letter_id),
            letter_name=letter.letter_name,
            template_path=letter.template_path,
            created_at=letter.created_at,
            updated_at=letter.updated_at
        )
        for letter in letters
    ]


@router.get("/types/{letter_id}", response_model=LetterResponse)
async def get_letter_type_endpoint(
    letter_id: str,
    db: Session = Depends(get_db)
):
    """Get letter type by ID"""
    letter = get_letter_by_id(db, letter_id)
    
    return LetterResponse(
        letter_id=str(letter.letter_id),
        letter_name=letter.letter_name,
        template_path=letter.template_path,
        created_at=letter.created_at,
        updated_at=letter.updated_at
    )


# ==================== Letter Transaction Endpoints ====================

@router.post("/requests", response_model=LetterTransactionResponse, status_code=201)
async def create_letter_request_endpoint(
    transaction_data: LetterTransactionCreate,
    user_id: str = Query(..., description="User ID (will be from auth middleware)"),
    db: Session = Depends(get_db)
):
    """Create new letter request (citizen)"""
    transaction = create_letter_transaction(db, user_id, transaction_data)
    
    applicant_name = None
    if transaction.user and transaction.user.resident:
        applicant_name = transaction.user.resident.name
    
    return LetterTransactionResponse(
        letter_transaction_id=str(transaction.letter_transaction_id),
        application_date=transaction.application_date,
        status=transaction.status,
        data=transaction.data,
        letter_result_path=transaction.letter_result_path,
        rejection_reason=transaction.rejection_reason,
        user_id=str(transaction.user_id),
        letter_id=str(transaction.letter_id),
        letter_name=transaction.letter.letter_name if transaction.letter else None,
        applicant_name=applicant_name,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.get("/requests", response_model=dict)
async def get_letter_requests_endpoint(
    filters: LetterTransactionFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get list of letter requests with filters (admin & user)"""
    total, transactions = get_letter_transactions(db, filters)
    
    data = []
    for transaction in transactions:
        applicant_name = None
        if transaction.user and transaction.user.resident:
            applicant_name = transaction.user.resident.name
        
        data.append(LetterTransactionResponse(
            letter_transaction_id=str(transaction.letter_transaction_id),
            application_date=transaction.application_date,
            status=transaction.status,
            data=transaction.data,
            letter_result_path=transaction.letter_result_path,
            rejection_reason=transaction.rejection_reason,
            user_id=str(transaction.user_id),
            letter_id=str(transaction.letter_id),
            letter_name=transaction.letter.letter_name if transaction.letter else None,
            applicant_name=applicant_name,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        ))
    
    return {"total": total, "data": data}


@router.get("/requests/{transaction_id}", response_model=LetterTransactionResponse)
async def get_letter_request_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get letter request by ID"""
    transaction = get_transaction_by_id(db, transaction_id)
    
    applicant_name = None
    if transaction.user and transaction.user.resident:
        applicant_name = transaction.user.resident.name
    
    return LetterTransactionResponse(
        letter_transaction_id=str(transaction.letter_transaction_id),
        application_date=transaction.application_date,
        status=transaction.status,
        data=transaction.data,
        letter_result_path=transaction.letter_result_path,
        rejection_reason=transaction.rejection_reason,
        user_id=str(transaction.user_id),
        letter_id=str(transaction.letter_id),
        letter_name=transaction.letter.letter_name if transaction.letter else None,
        applicant_name=applicant_name,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.patch("/requests/{transaction_id}/status", response_model=LetterTransactionResponse)
async def update_request_status_endpoint(
    transaction_id: str,
    approval: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve or reject letter request (admin only) - PDF generated on approval"""
    transaction = update_transaction_status(db, transaction_id, approval)
    
    applicant_name = None
    if transaction.user and transaction.user.resident:
        applicant_name = transaction.user.resident.name
    
    return LetterTransactionResponse(
        letter_transaction_id=str(transaction.letter_transaction_id),
        application_date=transaction.application_date,
        status=transaction.status,
        data=transaction.data,
        letter_result_path=transaction.letter_result_path,
        rejection_reason=transaction.rejection_reason,
        user_id=str(transaction.user_id),
        letter_id=str(transaction.letter_id),
        letter_name=transaction.letter.letter_name if transaction.letter else None,
        applicant_name=applicant_name,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )


@router.delete("/requests/{transaction_id}", status_code=204)
async def delete_letter_request_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Delete letter request"""
    delete_transaction(db, transaction_id)
    return None
