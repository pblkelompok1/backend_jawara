from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.core import Base
from datetime import datetime, timedelta, timezone

class RefreshSession(Base):
    __tablename__ = 'm_refresh_session'

    refresh_session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_token_hash = Column(String, unique=True, nullable=False)

    expires_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now() + timedelta(days=30)
    )
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now()
    )    
    revoked = Column(Boolean, unique=True, nullable=False, default=False)
    
    
    def __repr__(self):
        return f"<RefreshSession(refresh_session_id={self.refresh_session_id}, user_id={self.user_id}, revoked={self.revoked})>"
    