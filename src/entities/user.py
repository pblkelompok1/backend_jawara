from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from database.core import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    rw = "rw"          
    rt = "rt"     
    secretary = "secretary"
    treasurer = "treasurer"
    citizen = "citizen"

class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    pending = "pending"

class User(Base):
    __tablename__ = 'm_user'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False, default=UserRole.citizen.value)
    status = Column(String, nullable=False, default=UserStatus.pending.value)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, password_hash={self.password_hash}, role={self.role}, status={self.status})>"
