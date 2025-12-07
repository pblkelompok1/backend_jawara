import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID

class UserRole(str, enum.Enum):
    admin = "admin"
    citizen = "citizen"

class UserStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class UserModel(Base):
    __tablename__ = 'm_user'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String, nullable=False, default='citizen')
    status = Column(String, nullable=False, default='pending')
    resident_id = Column(UUID(as_uuid=True), ForeignKey('m_resident.resident_id'), nullable=True)

    # Relationships
    refresh_sessions = relationship('RefreshSessionModel', back_populates='user', foreign_keys='RefreshSessionModel.user_id')
    resident = relationship('ResidentModel', foreign_keys=[resident_id], back_populates='user')
    rt_rel = relationship('RTModel', back_populates='user_rel', uselist=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email='{self.email}', role='{self.role}', status='{self.status}')>"