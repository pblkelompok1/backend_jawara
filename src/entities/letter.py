import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class LetterStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LetterModel(Base):
    __tablename__ = 'm_letter'

    letter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    letter_name = Column(String, nullable=False)
    template_path = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship('LetterTransactionModel', back_populates='letter')

    def __repr__(self):
        return f"<LetterModel(id={self.letter_id}, name='{self.letter_name}')>"


class LetterTransactionModel(Base):
    __tablename__ = 't_letter_transaction'

    letter_transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="pending")
    data = Column(JSON, nullable=True)
    letter_result_path = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    letter_id = Column(UUID(as_uuid=True), ForeignKey('m_letter.letter_id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('UserModel', backref='letter_transactions')
    letter = relationship('LetterModel', back_populates='transactions')

    def __repr__(self):
        return f"<LetterTransactionModel(id={self.letter_transaction_id}, status='{self.status}')>"
