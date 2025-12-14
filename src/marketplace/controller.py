from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from src.database.core import get_db
from src.marketplace.schemas import (
    ProductCreate, ProductUpdate, ProductFilter, ProductResponse,
    TransactionCreate, TransactionFilter, TransactionResponse, TransactionStatusUpdate, TransactionItemResponse,
    RatingCreate, RatingUpdate, RatingResponse,
    TransactionMethodCreate, TransactionMethodUpdate, TransactionMethodResponse
)
from src.marketplace.service import (
    # Product services
    create_product, get_products, get_product_by_id, get_my_products,
    update_product, delete_product, add_product_images, increment_view_count, save_product_image,
    # Transaction services
    create_transaction, get_user_transactions, get_seller_transactions,
    get_transaction_by_id, update_transaction_status, cancel_transaction,
    # Rating services
    create_rating, get_product_ratings, get_my_ratings, update_rating, delete_rating,
    # Transaction method services
    create_transaction_method, get_transaction_methods, update_transaction_method
)
from sqlalchemy import func

router = APIRouter(
    prefix='/marketplace',
    tags=['Marketplace Service'],
)

# ==================== Product Endpoints ====================

@router.post("/products", response_model=ProductResponse)
async def create_product_endpoint(
    product_data: ProductCreate,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Create new product (seller)"""
    product = create_product(db, user_id, product_data)
    
    return ProductResponse(
        product_id=str(product.product_id),
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        view_count=product.view_count,
        description=product.description,
        more_detail=product.more_detail,
        images_path=product.images_path,
        user_id=str(product.user_id),
        created_at=product.created_at,
        updated_at=product.updated_at
    )

@router.get("/products", response_model=dict)
async def list_products_endpoint(
    filters: ProductFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get all products with filters"""
    total, products = get_products(db, filters)
    
    data = []
    for product in products:
        # Calculate average rating
        avg_rating = None
        total_ratings = 0
        if product.ratings:
            total_ratings = len(product.ratings)
            avg_rating = sum(r.rating_value for r in product.ratings) / total_ratings
        
        seller_name = None
        if product.user and product.user.resident:
            seller_name = product.user.resident.name
        
        data.append(ProductResponse(
            product_id=str(product.product_id),
            name=product.name,
            price=product.price,
            category=product.category,
            stock=product.stock,
            view_count=product.view_count,
            description=product.description,
            more_detail=product.more_detail,
            images_path=product.images_path,
            user_id=str(product.user_id),
            seller_name=seller_name,
            average_rating=round(avg_rating, 2) if avg_rating else None,
            total_ratings=total_ratings,
            created_at=product.created_at,
            updated_at=product.updated_at
        ))
    
    return {"total": total, "data": data}

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get product detail"""
    product = get_product_by_id(db, product_id)
    
    # Calculate average rating
    avg_rating = None
    total_ratings = 0
    if product.ratings:
        total_ratings = len(product.ratings)
        avg_rating = sum(r.rating_value for r in product.ratings) / total_ratings
    
    seller_name = None
    if product.user and product.user.resident:
        seller_name = product.user.resident.name
    
    return ProductResponse(
        product_id=str(product.product_id),
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        view_count=product.view_count,
        description=product.description,
        more_detail=product.more_detail,
        images_path=product.images_path,
        user_id=str(product.user_id),
        seller_name=seller_name,
        average_rating=round(avg_rating, 2) if avg_rating else None,
        total_ratings=total_ratings,
        created_at=product.created_at,
        updated_at=product.updated_at
    )

@router.get("/products/my-products/list", response_model=dict)
async def get_my_products_endpoint(
    user_id: str,  # TODO: Get from auth middleware
    filters: ProductFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get seller's products"""
    total, products = get_my_products(db, user_id, filters)
    
    data = []
    for product in products:
        avg_rating = None
        total_ratings = 0
        if product.ratings:
            total_ratings = len(product.ratings)
            avg_rating = sum(r.rating_value for r in product.ratings) / total_ratings
        
        data.append(ProductResponse(
            product_id=str(product.product_id),
            name=product.name,
            price=product.price,
            category=product.category,
            stock=product.stock,
            view_count=product.view_count,
            description=product.description,
            more_detail=product.more_detail,
            images_path=product.images_path,
            user_id=str(product.user_id),
            average_rating=round(avg_rating, 2) if avg_rating else None,
            total_ratings=total_ratings,
            created_at=product.created_at,
            updated_at=product.updated_at
        ))
    
    return {"total": total, "data": data}

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: str,
    product_data: ProductUpdate,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Update product (seller only)"""
    product = update_product(db, product_id, user_id, product_data)
    
    return ProductResponse(
        product_id=str(product.product_id),
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        view_count=product.view_count,
        description=product.description,
        more_detail=product.more_detail,
        images_path=product.images_path,
        user_id=str(product.user_id),
        created_at=product.created_at,
        updated_at=product.updated_at
    )

@router.delete("/products/{product_id}", status_code=204)
async def delete_product_endpoint(
    product_id: str,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Delete product (seller only)"""
    delete_product(db, product_id, user_id)
    return None

@router.post("/products/{product_id}/images", response_model=ProductResponse)
async def upload_product_images_endpoint(
    product_id: str,
    user_id: str,  # TODO: Get from auth middleware
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload product images"""
    image_paths = []
    for file in files:
        path = await save_product_image(file, product_id)
        image_paths.append(path)
    
    product = add_product_images(db, product_id, user_id, image_paths)
    
    return ProductResponse(
        product_id=str(product.product_id),
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        view_count=product.view_count,
        description=product.description,
        more_detail=product.more_detail,
        images_path=product.images_path,
        user_id=str(product.user_id),
        created_at=product.created_at,
        updated_at=product.updated_at
    )

@router.post("/products/{product_id}/view", status_code=204)
async def increment_product_view_endpoint(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Increment product view count"""
    increment_view_count(db, product_id)
    return None

# ==================== Transaction Endpoints ====================

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction_endpoint(
    transaction_data: TransactionCreate,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Create new transaction (buyer)"""
    transaction = create_transaction(db, user_id, transaction_data)
    
    items = []
    total_amount = 0
    for item in transaction.items:
        item_total = item.price_at_transaction * item.quantity
        total_amount += item_total
        items.append(TransactionItemResponse(
            product_id=str(item.product_id),
            product_name=item.product.name,
            quantity=item.quantity,
            price_at_transaction=item.price_at_transaction,
            total_price=item_total
        ))
    
    return TransactionResponse(
        product_transaction_id=str(transaction.product_transaction_id),
        address=transaction.address,
        description=transaction.description,
        status=transaction.status,
        user_id=str(transaction.user_id),
        transaction_method_id=transaction.transaction_method_id,
        transaction_method_name=transaction.transaction_method.method_name,
        items=items,
        total_amount=total_amount,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )

@router.get("/transactions", response_model=dict)
async def get_user_transactions_endpoint(
    user_id: str,  # TODO: Get from auth middleware
    filters: TransactionFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get user's transactions (buyer)"""
    total, transactions = get_user_transactions(db, user_id, filters)
    
    data = []
    for transaction in transactions:
        items = []
        total_amount = 0
        for item in transaction.items:
            item_total = item.price_at_transaction * item.quantity
            total_amount += item_total
            items.append(TransactionItemResponse(
                product_id=str(item.product_id),
                product_name=item.product.name,
                quantity=item.quantity,
                price_at_transaction=item.price_at_transaction,
                total_price=item_total
            ))
        
        data.append(TransactionResponse(
            product_transaction_id=str(transaction.product_transaction_id),
            address=transaction.address,
            description=transaction.description,
            status=transaction.status,
            user_id=str(transaction.user_id),
            transaction_method_id=transaction.transaction_method_id,
            transaction_method_name=transaction.transaction_method.method_name,
            items=items,
            total_amount=total_amount,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        ))
    
    return {"total": total, "data": data}

@router.get("/transactions/sales", response_model=dict)
async def get_seller_transactions_endpoint(
    user_id: str,  # TODO: Get from auth middleware
    filters: TransactionFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get seller's transactions"""
    total, transactions = get_seller_transactions(db, user_id, filters)
    
    data = []
    for transaction in transactions:
        items = []
        total_amount = 0
        for item in transaction.items:
            item_total = item.price_at_transaction * item.quantity
            total_amount += item_total
            items.append(TransactionItemResponse(
                product_id=str(item.product_id),
                product_name=item.product.name,
                quantity=item.quantity,
                price_at_transaction=item.price_at_transaction,
                total_price=item_total
            ))
        
        buyer_name = None
        if transaction.user and transaction.user.resident:
            buyer_name = transaction.user.resident.name
        
        data.append(TransactionResponse(
            product_transaction_id=str(transaction.product_transaction_id),
            address=transaction.address,
            description=transaction.description,
            status=transaction.status,
            user_id=str(transaction.user_id),
            buyer_name=buyer_name,
            transaction_method_id=transaction.transaction_method_id,
            transaction_method_name=transaction.transaction_method.method_name,
            items=items,
            total_amount=total_amount,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        ))
    
    return {"total": total, "data": data}

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get transaction detail"""
    transaction = get_transaction_by_id(db, transaction_id)
    
    items = []
    total_amount = 0
    for item in transaction.items:
        item_total = item.price_at_transaction * item.quantity
        total_amount += item_total
        items.append(TransactionItemResponse(
            product_id=str(item.product_id),
            product_name=item.product.name,
            quantity=item.quantity,
            price_at_transaction=item.price_at_transaction,
            total_price=item_total
        ))
    
    buyer_name = None
    if transaction.user and transaction.user.resident:
        buyer_name = transaction.user.resident.name
    
    return TransactionResponse(
        product_transaction_id=str(transaction.product_transaction_id),
        address=transaction.address,
        description=transaction.description,
        status=transaction.status,
        user_id=str(transaction.user_id),
        buyer_name=buyer_name,
        transaction_method_id=transaction.transaction_method_id,
        transaction_method_name=transaction.transaction_method.method_name,
        items=items,
        total_amount=total_amount,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )

@router.put("/transactions/{transaction_id}/status", response_model=TransactionResponse)
async def update_transaction_status_endpoint(
    transaction_id: str,
    status_data: TransactionStatusUpdate,
    user_id: str,  # TODO: Get from auth middleware (seller)
    db: Session = Depends(get_db)
):
    """Update transaction status (seller only)"""
    transaction = update_transaction_status(db, transaction_id, user_id, status_data)
    
    items = []
    total_amount = 0
    for item in transaction.items:
        item_total = item.price_at_transaction * item.quantity
        total_amount += item_total
        items.append(TransactionItemResponse(
            product_id=str(item.product_id),
            product_name=item.product.name,
            quantity=item.quantity,
            price_at_transaction=item.price_at_transaction,
            total_price=item_total
        ))
    
    return TransactionResponse(
        product_transaction_id=str(transaction.product_transaction_id),
        address=transaction.address,
        description=transaction.description,
        status=transaction.status,
        user_id=str(transaction.user_id),
        transaction_method_id=transaction.transaction_method_id,
        transaction_method_name=transaction.transaction_method.method_name,
        items=items,
        total_amount=total_amount,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )

@router.delete("/transactions/{transaction_id}", status_code=204)
async def cancel_transaction_endpoint(
    transaction_id: str,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Cancel transaction (buyer only, if pending)"""
    cancel_transaction(db, transaction_id, user_id)
    return None

# ==================== Rating Endpoints ====================

@router.post("/products/{product_id}/ratings", response_model=RatingResponse)
async def create_rating_endpoint(
    product_id: str,
    rating_data: RatingCreate,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Create product rating"""
    rating = create_rating(db, product_id, user_id, rating_data)
    
    user_name = None
    if rating.user and rating.user.resident:
        user_name = rating.user.resident.name
    
    return RatingResponse(
        rating_id=str(rating.rating_id),
        product_id=str(rating.product_id),
        user_id=str(rating.user_id),
        user_name=user_name,
        rating_value=rating.rating_value,
        description=rating.description,
        created_at=rating.created_at,
        updated_at=rating.updated_at
    )

@router.get("/products/{product_id}/ratings", response_model=List[RatingResponse])
async def get_product_ratings_endpoint(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get all ratings for a product"""
    ratings = get_product_ratings(db, product_id)
    
    return [
        RatingResponse(
            rating_id=str(rating.rating_id),
            product_id=str(rating.product_id),
            user_id=str(rating.user_id),
            user_name=rating.user.resident.name if rating.user and rating.user.resident else None,
            rating_value=rating.rating_value,
            description=rating.description,
            created_at=rating.created_at,
            updated_at=rating.updated_at
        )
        for rating in ratings
    ]

@router.get("/ratings/my-ratings", response_model=List[RatingResponse])
async def get_my_ratings_endpoint(
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Get user's ratings"""
    ratings = get_my_ratings(db, user_id)
    
    return [
        RatingResponse(
            rating_id=str(rating.rating_id),
            product_id=str(rating.product_id),
            user_id=str(rating.user_id),
            rating_value=rating.rating_value,
            description=rating.description,
            created_at=rating.created_at,
            updated_at=rating.updated_at
        )
        for rating in ratings
    ]

@router.put("/ratings/{rating_id}", response_model=RatingResponse)
async def update_rating_endpoint(
    rating_id: str,
    rating_data: RatingUpdate,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Update own rating"""
    rating = update_rating(db, rating_id, user_id, rating_data)
    
    user_name = None
    if rating.user and rating.user.resident:
        user_name = rating.user.resident.name
    
    return RatingResponse(
        rating_id=str(rating.rating_id),
        product_id=str(rating.product_id),
        user_id=str(rating.user_id),
        user_name=user_name,
        rating_value=rating.rating_value,
        description=rating.description,
        created_at=rating.created_at,
        updated_at=rating.updated_at
    )

@router.delete("/ratings/{rating_id}", status_code=204)
async def delete_rating_endpoint(
    rating_id: str,
    user_id: str,  # TODO: Get from auth middleware
    db: Session = Depends(get_db)
):
    """Delete own rating"""
    delete_rating(db, rating_id, user_id)
    return None

# ==================== Transaction Method Endpoints ====================

@router.post("/transaction-methods", response_model=TransactionMethodResponse)
async def create_transaction_method_endpoint(
    method_data: TransactionMethodCreate,
    db: Session = Depends(get_db)
):
    """Create transaction method (admin only)"""
    method = create_transaction_method(db, method_data)
    
    return TransactionMethodResponse(
        transaction_method_id=method.transaction_method_id,
        method_name=method.method_name,
        description=method.description,
        is_active=method.is_active,
        created_at=method.created_at,
        updated_at=method.updated_at
    )

@router.get("/transaction-methods", response_model=List[TransactionMethodResponse])
async def get_transaction_methods_endpoint(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all transaction methods"""
    methods = get_transaction_methods(db, active_only)
    
    return [
        TransactionMethodResponse(
            transaction_method_id=method.transaction_method_id,
            method_name=method.method_name,
            description=method.description,
            is_active=method.is_active,
            created_at=method.created_at,
            updated_at=method.updated_at
        )
        for method in methods
    ]

@router.put("/transaction-methods/{method_id}", response_model=TransactionMethodResponse)
async def update_transaction_method_endpoint(
    method_id: int,
    method_data: TransactionMethodUpdate,
    db: Session = Depends(get_db)
):
    """Update transaction method (admin only)"""
    method = update_transaction_method(db, method_id, method_data)
    
    return TransactionMethodResponse(
        transaction_method_id=method.transaction_method_id,
        method_name=method.method_name,
        description=method.description,
        is_active=method.is_active,
        created_at=method.created_at,
        updated_at=method.updated_at
    )
