from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== Product Schemas ====================

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: int = Field(..., gt=0)
    category: str
    stock: int = Field(default=0, ge=0)
    description: Optional[str] = None
    more_detail: Optional[dict] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    more_detail: Optional[dict] = None
    images_path: Optional[List[str]] = None

class ProductFilter(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class ProductResponse(BaseModel):
    product_id: str
    name: str
    price: int
    category: str
    stock: int
    view_count: int
    status: str = "active"
    sold_count: int = 0
    description: Optional[str]
    more_detail: Optional[dict]
    images_path: Optional[List[str]]
    user_id: str
    seller_name: Optional[str] = None
    average_rating: Optional[float] = None
    total_ratings: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ==================== Transaction Schemas ====================

class TransactionItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class TransactionCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    transaction_method_id: int
    is_cod: bool = False
    items: List[TransactionItemCreate] = Field(..., min_items=1)

class TransactionStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PROSES|SEDANG_DIKIRIM|SELESAI|DITOLAK)$")

class TransactionFilter(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None  # "active" or "history"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class TransactionItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price_at_transaction: int
    total_price: int

    class Config:
        orm_mode = True

class TransactionResponse(BaseModel):
    product_transaction_id: str
    address: str
    description: Optional[str]
    status: str
    total_price: int
    payment_proof_path: Optional[str] = None
    is_cod: bool
    user_id: str
    buyer_name: Optional[str] = None
    transaction_method_id: int
    transaction_method_name: Optional[str] = None
    items: List[TransactionItemResponse]
    total_amount: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ==================== Rating Schemas ====================

class RatingCreate(BaseModel):
    rating_value: int = Field(..., ge=1, le=5)
    description: Optional[str] = None

class RatingUpdate(BaseModel):
    rating_value: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None

class RatingResponse(BaseModel):
    rating_id: str
    product_id: str
    user_id: str
    user_name: Optional[str] = None
    rating_value: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ==================== Transaction Method Schemas ====================

class TransactionMethodCreate(BaseModel):
    method_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

class TransactionMethodUpdate(BaseModel):
    method_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class TransactionMethodResponse(BaseModel):
    transaction_method_id: int
    method_name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
