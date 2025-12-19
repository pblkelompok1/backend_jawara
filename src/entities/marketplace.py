import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, SmallInteger, Text, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from src.database.core import Base
from datetime import datetime
import enum


class ProductCategoryEnum(str, enum.Enum):
    MAKANAN = "Makanan"
    PAKAIAN = "Pakaian"
    BAHAN_MASAK = "Bahan Masak"
    JASA = "Jasa"
    ELEKTRONIK = "Elektronik"


class TransactionStatusEnum(enum.Enum):
    BELUM_DIBAYAR = "BELUM_DIBAYAR"
    PROSES = "PROSES"
    SIAP_DIAMBIL = "SIAP_DIAMBIL"
    SEDANG_DIKIRIM = "SEDANG_DIKIRIM"
    SELESAI = "SELESAI"
    DITOLAK = "DITOLAK"


class TransactionMethodModel(Base):
    __tablename__ = 'm_transaction_method'

    transaction_method_id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship('ProductTransactionModel', back_populates='transaction_method')

    def __repr__(self):
        return f"<TransactionMethodModel(id={self.transaction_method_id}, name='{self.method_name}')>"


class ProductModel(Base):
    __tablename__ = 'm_product'

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(Enum(ProductCategoryEnum), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")
    sold_count = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    more_detail = Column(JSON, nullable=True)
    images_path = Column(ARRAY(String), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('UserModel', back_populates='products')
    transaction_items = relationship('ListProductTransactionModel', back_populates='product')
    ratings = relationship('ProductRatingModel', back_populates='product')

    def __repr__(self):
        return f"<ProductModel(id={self.product_id}, name='{self.name}', price={self.price})>"


class ProductTransactionModel(Base):
    __tablename__ = 't_product_transaction'

    product_transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Enum(TransactionStatusEnum), nullable=False, default=TransactionStatusEnum.BELUM_DIBAYAR)
    total_price = Column(Integer, nullable=False, default=0)
    payment_proof_path = Column(String(500), nullable=True)
    is_cod = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    transaction_method_id = Column(Integer, ForeignKey('m_transaction_method.transaction_method_id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('UserModel', back_populates='product_transactions')
    transaction_method = relationship('TransactionMethodModel', back_populates='transactions')
    items = relationship('ListProductTransactionModel', back_populates='transaction')

    def __repr__(self):
        return f"<ProductTransactionModel(id={self.product_transaction_id}, status='{self.status}')>"


class ListProductTransactionModel(Base):
    __tablename__ = 't_list_product_transaction'

    product_id = Column(UUID(as_uuid=True), ForeignKey('m_product.product_id'), primary_key=True)
    product_transaction_id = Column(UUID(as_uuid=True), ForeignKey('t_product_transaction.product_transaction_id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_transaction = Column(Integer, nullable=False)

    # Relationships
    product = relationship('ProductModel', back_populates='transaction_items')
    transaction = relationship('ProductTransactionModel', back_populates='items')

    def __repr__(self):
        return f"<ListProductTransactionModel(product={self.product_id}, quantity={self.quantity})>"


class ProductRatingModel(Base):
    __tablename__ = 't_product_rating'
    __table_args__ = (
        CheckConstraint('rating_value >= 1 AND rating_value <= 5', name='check_rating_value_range'),
    )

    rating_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('m_product.product_id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    rating_value = Column(SmallInteger, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship('ProductModel', back_populates='ratings')
    user = relationship('UserModel', back_populates='product_ratings')

    def __repr__(self):
        return f"<ProductRatingModel(id={self.rating_id}, product={self.product_id}, rating={self.rating_value})>"
