from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.core import get_db
from src.admin import service
from src.admin.schemas import (
    AdminStatisticsResponse, AdminStatisticsOut,
    FinanceSummaryResponse, FinanceSummaryOut,
    ErrorResponse
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"], redirect_slashes=False)


# ==================== Admin Statistics Endpoint ====================

@router.get(
    "/statistics",
    response_model=AdminStatisticsResponse,
    responses={
        200: {"description": "Successfully retrieved admin statistics"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        403: {"model": ErrorResponse, "description": "Forbidden - User is not admin"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get Admin Dashboard Statistics",
    description="""
    Retrieve comprehensive statistics for admin dashboard including:
    - Total number of approved residents
    - Number of active users (logged in within 30 days)
    - Pending registration requests waiting for approval
    - Number of reports submitted today
    - Number of pending letter requests
    
    **Authorization Required:** Admin role only
    """
)
def get_admin_statistics(
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency when auth is implemented
    # current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get admin dashboard statistics.
    
    **Access Control:**
    - Requires valid JWT token
    - User must have 'admin', 'rt', or 'rw' role
    
    **Returns:**
    - totalResidents: Total approved citizens in the system
    - activeUsers: Users who logged in within last 30 days
    - pendingRegistrations: Users waiting for admin approval
    - newReportsToday: Reports created today
    - pendingLetters: Letter requests with pending status
    """
    try:
        # TODO: Add role validation
        # if current_user.role not in ['admin', 'rt', 'rw']:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied. Admin role required."
        #     )
        
        stats_data = service.get_admin_statistics(db)
        
        return AdminStatisticsResponse(
            success=True,
            data=AdminStatisticsOut(**stats_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


# ==================== Finance Summary Endpoint ====================

@router.get(
    "/finance/summary",
    response_model=FinanceSummaryResponse,
    responses={
        200: {"description": "Successfully retrieved finance summary"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing token"},
        403: {"model": ErrorResponse, "description": "Forbidden - User is not admin"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get Finance Summary for Admin Dashboard",
    description="""
    Retrieve financial summary including:
    - Total income from all paid transactions
    - Total expenses
    - Current balance (income - expense)
    - Total number of transactions
    
    All amounts are in Indonesian Rupiah (IDR).
    
    **Authorization Required:** Admin role only
    """
)
def get_finance_summary(
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency when auth is implemented
    # current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get finance summary for admin dashboard.
    
    **Access Control:**
    - Requires valid JWT token
    - User must have 'admin', 'rt', or 'rw' role
    
    **Returns:**
    - totalIncome: Sum of all paid fee transactions (IDR)
    - totalExpense: Sum of all expenses (IDR) - currently 0 if not tracked
    - balance: totalIncome - totalExpense (IDR)
    - transactionCount: Total number of all transactions
    
    **Note:** 
    - All values are in Rupiah (IDR) without separators
    - Frontend should format as: Rp 15.750.000 (with thousand separators)
    """
    try:
        # TODO: Add role validation
        # if current_user.role not in ['admin', 'rt', 'rw']:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied. Admin role required."
        #     )
        
        finance_data = service.get_finance_summary(db)
        
        return FinanceSummaryResponse(
            success=True,
            data=FinanceSummaryOut(**finance_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve finance summary: {str(e)}"
        )


# ==================== Health Check for Admin Module ====================

@router.get(
    "/health",
    summary="Admin Module Health Check",
    description="Simple endpoint to verify admin module is working"
)
def admin_health_check():
    """Health check endpoint for admin module"""
    return {
        "status": "healthy",
        "module": "admin",
        "endpoints": [
            "/admin/statistics",
            "/admin/finance/summary"
        ]
    }
