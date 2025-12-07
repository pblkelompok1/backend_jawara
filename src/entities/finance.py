import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class PaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    pending = "pending"
    paid = "paid"
    
class AutomationMode(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"
    
class TransactionMethod(str, enum.Enum):
    cash = "cash"
    qris = "qris"

# Entity untuk m_fee
class FeeModel(Base):
	__tablename__ = 'm_fee'

	fee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	fee_name = Column(String(255), nullable=False)
	amount = Column(Integer, nullable=False)
	charge_date = Column(Date, nullable=True)
	description = Column(String, nullable=True)
	fee_category = Column(String, nullable=False)
	automation_mode = Column(String, nullable=True, default=AutomationMode.monthly.value)

	transactions = relationship('FeeTransactionModel', back_populates='fee_rel')

	def __repr__(self):
		return f"<FeeModel(fee_id={self.fee_id}, fee_name={self.fee_name}, amount={self.amount})>"

# Entity untuk t_fee_transaction
class FeeTransactionModel(Base):
	__tablename__ = 't_fee_transaction'

	fee_transaction_id = Column(Integer, primary_key=True, autoincrement=True)
	transaction_date = Column(Date, nullable=True)
	fee_id = Column(UUID(as_uuid=True), ForeignKey('m_fee.fee_id'), nullable=False)
	transaction_method = Column(String, nullable=False, default=TransactionMethod.cash.value)
	status = Column(String, nullable=False, default=PaymentStatus.unpaid.value)
	family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)
	evidence_path = Column(String, nullable=False)

	fee_rel = relationship('FeeModel', back_populates='transactions')
	# family_rel = relationship('FamilyModel') # Uncomment jika FamilyModel tersedia

	def __repr__(self):
		return f"<FeeTransactionModel(fee_transaction_id={self.fee_transaction_id}, fee_id={self.fee_id}, family_id={self.family_id})>"

# Entity untuk t_finance_transaction
class FinanceTransactionModel(Base):
	__tablename__ = 't_finance_transaction'

	finance_transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(String, nullable=False)
	amount = Column(Integer, nullable=False)
	category = Column(String, nullable=False)
	transaction_date = Column(Date, nullable=True)
	evidence_path = Column(String, nullable=False)

	def __repr__(self):
		return f"<FinanceTransactionModel(finance_transaction_id={self.finance_transaction_id}, name={self.name}, amount={self.amount})>"
