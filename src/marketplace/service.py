from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, UploadFile
from src.entities.marketplace import (
    ProductModel, ProductTransactionModel, ListProductTransactionModel,
    ProductRatingModel, TransactionMethodModel, TransactionStatusEnum
)
from src.entities.user import UserModel
from src.entities.resident import ResidentModel
from src.marketplace.schemas import (
    ProductCreate, ProductUpdate, ProductFilter,
    TransactionCreate, TransactionFilter, TransactionStatusUpdate,
    RatingCreate, RatingUpdate,
    TransactionMethodCreate, TransactionMethodUpdate
)
import uuid as uuid_lib
from pathlib import Path
import os
from datetime import datetime

# ==================== File Upload Helper ====================

async def save_product_image(file: UploadFile, product_id: str) -> str:
    """Save product image and return storage path"""
    storage_dir = Path("storage/default/product_banner")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{product_id}_{uuid_lib.uuid4()}{file_extension}"
    file_path = storage_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return str(file_path).replace("\\", "/")

# ==================== Product Services ====================

def create_product(db: Session, user_id: str, product_data: ProductCreate) -> ProductModel:
    """Create new product"""
    product = ProductModel(
        user_id=uuid_lib.UUID(user_id),
        name=product_data.name,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
        description=product_data.description,
        more_detail=product_data.more_detail,
        images_path=[]
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_products(db: Session, filters: ProductFilter) -> Tuple[int, List[ProductModel]]:
    """Get list of products with filters and pagination"""
    query = db.query(ProductModel).options(
        joinedload(ProductModel.user).joinedload(UserModel.resident),
        joinedload(ProductModel.ratings)
    )
    
    # Apply filters
    if filters.name:
        query = query.filter(ProductModel.name.ilike(f"%{filters.name}%"))
    if filters.category:
        query = query.filter(ProductModel.category == filters.category)
    
    total = query.count()
    results = query.order_by(ProductModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results

def get_product_by_id(db: Session, product_id: str) -> ProductModel:
    """Get product by ID with ratings"""
    product = db.query(ProductModel).options(
        joinedload(ProductModel.user).joinedload(UserModel.resident),
        joinedload(ProductModel.ratings).joinedload(ProductRatingModel.user).joinedload(UserModel.resident)
    ).filter(ProductModel.product_id == uuid_lib.UUID(product_id)).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def get_my_products(db: Session, user_id: str, filters: ProductFilter) -> Tuple[int, List[ProductModel]]:
    """Get seller's products"""
    query = db.query(ProductModel).options(
        joinedload(ProductModel.ratings)
    ).filter(ProductModel.user_id == uuid_lib.UUID(user_id))
    
    if filters.name:
        query = query.filter(ProductModel.name.ilike(f"%{filters.name}%"))
    if filters.category:
        query = query.filter(ProductModel.category == filters.category)
    
    total = query.count()
    results = query.order_by(ProductModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results

def update_product(db: Session, product_id: str, user_id: str, product_data: ProductUpdate) -> ProductModel:
    """Update product (only owner can update)"""
    product = db.query(ProductModel).filter(
        and_(
            ProductModel.product_id == uuid_lib.UUID(product_id),
            ProductModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")
    
    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: str, user_id: str) -> None:
    """Delete product (only owner can delete)"""
    product = db.query(ProductModel).filter(
        and_(
            ProductModel.product_id == uuid_lib.UUID(product_id),
            ProductModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")
    
    db.delete(product)
    db.commit()

def add_product_images(db: Session, product_id: str, user_id: str, image_paths: List[str]) -> ProductModel:
    """Add images to product"""
    product = db.query(ProductModel).filter(
        and_(
            ProductModel.product_id == uuid_lib.UUID(product_id),
            ProductModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")
    
    current_images = product.images_path or []
    product.images_path = current_images + image_paths
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product

def increment_view_count(db: Session, product_id: str) -> None:
    """Increment product view count"""
    product = db.query(ProductModel).filter(ProductModel.product_id == uuid_lib.UUID(product_id)).first()
    if product:
        product.view_count += 1
        db.commit()

# ==================== Transaction Services ====================

def create_transaction(db: Session, user_id: str, transaction_data: TransactionCreate) -> ProductTransactionModel:
    """Create new transaction"""
    # Verify transaction method exists
    method = db.query(TransactionMethodModel).filter(
        and_(
            TransactionMethodModel.transaction_method_id == transaction_data.transaction_method_id,
            TransactionMethodModel.is_active == True
        )
    ).first()
    if not method:
        raise HTTPException(status_code=404, detail="Transaction method not found or inactive")
    
    # Create transaction
    transaction = ProductTransactionModel(
        user_id=uuid_lib.UUID(user_id),
        address=transaction_data.address,
        description=transaction_data.description,
        transaction_method_id=transaction_data.transaction_method_id,
        is_cod=transaction_data.is_cod,
        status=TransactionStatusEnum.BELUM_DIBAYAR
    )
    db.add(transaction)
    db.flush()
    
    # Add transaction items and calculate total
    total_amount = 0
    for item in transaction_data.items:
        product = db.query(ProductModel).filter(ProductModel.product_id == uuid_lib.UUID(item.product_id)).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        
        transaction_item = ListProductTransactionModel(
            product_id=uuid_lib.UUID(item.product_id),
            product_transaction_id=transaction.product_transaction_id,
            quantity=item.quantity,
            price_at_transaction=product.price
        )
        db.add(transaction_item)
        total_amount += product.price * item.quantity
    
    # Set total_price
    transaction.total_price = total_amount
    
    db.commit()
    db.refresh(transaction)
    return transaction

def get_user_transactions(db: Session, user_id: str, filters: TransactionFilter) -> Tuple[int, List[ProductTransactionModel]]:
    """Get user's transactions (as buyer)"""
    query = db.query(ProductTransactionModel).options(
        joinedload(ProductTransactionModel.transaction_method),
        joinedload(ProductTransactionModel.items).joinedload(ListProductTransactionModel.product)
    ).filter(ProductTransactionModel.user_id == uuid_lib.UUID(user_id))
    
    if filters.status:
        query = query.filter(ProductTransactionModel.status == filters.status)
    
    total = query.count()
    results = query.order_by(ProductTransactionModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results

def get_seller_transactions(db: Session, seller_id: str, filters: TransactionFilter) -> Tuple[int, List[ProductTransactionModel]]:
    """Get seller's transactions"""
    query = db.query(ProductTransactionModel).options(
        joinedload(ProductTransactionModel.user).joinedload(UserModel.resident),
        joinedload(ProductTransactionModel.transaction_method),
        joinedload(ProductTransactionModel.items).joinedload(ListProductTransactionModel.product)
    ).join(
        ListProductTransactionModel,
        ProductTransactionModel.product_transaction_id == ListProductTransactionModel.product_transaction_id
    ).join(
        ProductModel,
        ListProductTransactionModel.product_id == ProductModel.product_id
    ).filter(ProductModel.user_id == uuid_lib.UUID(seller_id))
    
    # Filter by type
    if filters.type == "active":
        query = query.filter(ProductTransactionModel.status.in_([
            TransactionStatusEnum.BELUM_DIBAYAR,
            TransactionStatusEnum.PROSES,
            TransactionStatusEnum.SIAP_DIAMBIL,
            TransactionStatusEnum.SEDANG_DIKIRIM
        ]))
    elif filters.type == "history":
        query = query.filter(ProductTransactionModel.status.in_([
            TransactionStatusEnum.SELESAI,
            TransactionStatusEnum.DITOLAK
        ]))
    elif filters.status:
        query = query.filter(ProductTransactionModel.status == filters.status)
    
    query = query.distinct()
    total = query.count()
    results = query.order_by(ProductTransactionModel.created_at.desc()).offset(filters.offset).limit(filters.limit).all()
    
    return total, results

def get_transaction_by_id(db: Session, transaction_id: str) -> ProductTransactionModel:
    """Get transaction by ID"""
    transaction = db.query(ProductTransactionModel).options(
        joinedload(ProductTransactionModel.user).joinedload(UserModel.resident),
        joinedload(ProductTransactionModel.transaction_method),
        joinedload(ProductTransactionModel.items).joinedload(ListProductTransactionModel.product)
    ).filter(ProductTransactionModel.product_transaction_id == uuid_lib.UUID(transaction_id)).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

def update_transaction_status(db: Session, transaction_id: str, seller_id: str, status_data: TransactionStatusUpdate) -> ProductTransactionModel:
    """Update transaction status (seller only)"""
    transaction = db.query(ProductTransactionModel).options(
        joinedload(ProductTransactionModel.items).joinedload(ListProductTransactionModel.product)
    ).filter(ProductTransactionModel.product_transaction_id == uuid_lib.UUID(transaction_id)).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Authorization check removed - allow any user to update transaction status
    
    old_status = transaction.status
    transaction.status = TransactionStatusEnum[status_data.status]
    transaction.updated_at = datetime.utcnow()
    
    # Reduce stock and increment sold_count when status becomes completed
    if status_data.status == 'SELESAI' and old_status != TransactionStatusEnum.SELESAI:
        for item in transaction.items:
            product = item.product
            product.stock -= item.quantity
            if product.stock < 0:
                product.stock = 0
            product.sold_count += item.quantity
    
    db.commit()
    db.refresh(transaction)
    return transaction

def cancel_transaction(db: Session, transaction_id: str, user_id: str) -> ProductTransactionModel:
    """Cancel transaction (buyer only, if status is pending)"""
    transaction = db.query(ProductTransactionModel).filter(
        and_(
            ProductTransactionModel.product_transaction_id == uuid_lib.UUID(transaction_id),
            ProductTransactionModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")
    
    if transaction.status != TransactionStatusEnum.BELUM_DIBAYAR:
        raise HTTPException(status_code=400, detail="Can only cancel pending transactions")
    
    transaction.status = TransactionStatusEnum.DITOLAK
    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    return transaction

# ==================== Rating Services ====================

def create_rating(db: Session, product_id: str, user_id: str, rating_data: RatingCreate) -> ProductRatingModel:
    """Create product rating"""
    # Check if product exists
    product = db.query(ProductModel).filter(ProductModel.product_id == uuid_lib.UUID(product_id)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already rated this product
    existing_rating = db.query(ProductRatingModel).filter(
        and_(
            ProductRatingModel.product_id == uuid_lib.UUID(product_id),
            ProductRatingModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if existing_rating:
        raise HTTPException(status_code=400, detail="You have already rated this product")
    
    rating = ProductRatingModel(
        product_id=uuid_lib.UUID(product_id),
        user_id=uuid_lib.UUID(user_id),
        rating_value=rating_data.rating_value,
        description=rating_data.description
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

def get_product_ratings(db: Session, product_id: str) -> List[ProductRatingModel]:
    """Get all ratings for a product"""
    ratings = db.query(ProductRatingModel).options(
        joinedload(ProductRatingModel.user).joinedload(UserModel.resident)
    ).filter(ProductRatingModel.product_id == uuid_lib.UUID(product_id)).order_by(
        ProductRatingModel.created_at.desc()
    ).all()
    return ratings

def get_my_ratings(db: Session, user_id: str) -> List[ProductRatingModel]:
    """Get user's ratings"""
    ratings = db.query(ProductRatingModel).options(
        joinedload(ProductRatingModel.product)
    ).filter(ProductRatingModel.user_id == uuid_lib.UUID(user_id)).order_by(
        ProductRatingModel.created_at.desc()
    ).all()
    return ratings

def update_rating(db: Session, rating_id: str, user_id: str, rating_data: RatingUpdate) -> ProductRatingModel:
    """Update own rating"""
    rating = db.query(ProductRatingModel).filter(
        and_(
            ProductRatingModel.rating_id == uuid_lib.UUID(rating_id),
            ProductRatingModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found or unauthorized")
    
    update_data = rating_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rating, key, value)
    
    rating.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rating)
    return rating

def delete_rating(db: Session, rating_id: str, user_id: str) -> None:
    """Delete own rating"""
    rating = db.query(ProductRatingModel).filter(
        and_(
            ProductRatingModel.rating_id == uuid_lib.UUID(rating_id),
            ProductRatingModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found or unauthorized")
    
    db.delete(rating)
    db.commit()

# ==================== Transaction Method Services ====================

def create_transaction_method(db: Session, method_data: TransactionMethodCreate) -> TransactionMethodModel:
    """Create transaction method (admin only)"""
    method = TransactionMethodModel(
        method_name=method_data.method_name,
        description=method_data.description,
        is_active=method_data.is_active
    )
    db.add(method)
    db.commit()
    db.refresh(method)
    return method

def get_transaction_methods(db: Session, active_only: bool = True) -> List[TransactionMethodModel]:
    """Get all transaction methods"""
    query = db.query(TransactionMethodModel)
    if active_only:
        query = query.filter(TransactionMethodModel.is_active == True)
    return query.all()

def update_transaction_method(db: Session, method_id: int, method_data: TransactionMethodUpdate) -> TransactionMethodModel:
    """Update transaction method (admin only)"""
    method = db.query(TransactionMethodModel).filter(
        TransactionMethodModel.transaction_method_id == method_id
    ).first()
    
    if not method:
        raise HTTPException(status_code=404, detail="Transaction method not found")
    
    update_data = method_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(method, key, value)
    
    method.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(method)
    return method

# ==================== Payment Proof Upload ====================

async def upload_payment_proof(db: Session, transaction_id: str, user_id: str, file: UploadFile) -> ProductTransactionModel:
    """Upload payment proof (images and PDF allowed) and change status to PROSES"""
    # Verify transaction belongs to user
    transaction = db.query(ProductTransactionModel).filter(
        and_(
            ProductTransactionModel.product_transaction_id == uuid_lib.UUID(transaction_id),
            ProductTransactionModel.user_id == uuid_lib.UUID(user_id)
        )
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")
    
    # Only allow upload if transaction is not completed or rejected
    if transaction.status in [TransactionStatusEnum.SELESAI, TransactionStatusEnum.DITOLAK]:
        raise HTTPException(status_code=400, detail="Cannot upload proof for completed/rejected transaction")
    
    # Validate file type - Allow images and PDF only
    allowed_image_types = [
        "image/jpeg", "image/jpg", "image/png", "image/webp", 
        "image/gif", "image/bmp", "image/tiff", "image/svg+xml"
    ]
    allowed_pdf_types = ["application/pdf"]
    allowed_types = allowed_image_types + allowed_pdf_types
    
    allowed_image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"]
    allowed_pdf_extensions = [".pdf"]
    allowed_extensions = allowed_image_extensions + allowed_pdf_extensions
    
    # Blocked types (Word, PowerPoint, Excel, etc.)
    blocked_types = [
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-powerpoint",  # .ppt
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/zip",  # .zip
        "application/x-rar-compressed",  # .rar
        "text/plain",  # .txt
    ]
    
    # Get file extension
    file_ext = None
    if file.filename:
        file_ext = "." + file.filename.split(".")[-1].lower()
    
    # Check if blocked
    if file.content_type and file.content_type.lower() in blocked_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {file.content_type}. Only images and PDF are accepted."
        )
    
    # Check both content_type and extension
    content_type_valid = file.content_type and file.content_type.lower() in allowed_types
    extension_valid = file_ext and file_ext in allowed_extensions
    
    if not (content_type_valid or extension_valid):
        raise HTTPException(
            status_code=400,
            detail=f"Only images (JPEG, PNG, WEBP, GIF, BMP, TIFF, SVG) and PDF are allowed. Received: {file.content_type}, Extension: {file_ext}"
        )
    
    # Save file
    storage_dir = Path("storage/finance/payment_proof")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Use file extension from filename, or default based on content type
    if not file_ext:
        if file.content_type == "application/pdf":
            ext = ".pdf"
        else:
            ext = ".jpg"
    else:
        ext = file_ext
    
    unique_filename = f"{transaction_id}_{uuid_lib.uuid4()}{ext}"
    file_path = storage_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update transaction with payment proof and change status to Proses
    transaction.payment_proof_path = str(file_path).replace("\\", "/")
    transaction.status = TransactionStatusEnum.PROSES
    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    
    return transaction
