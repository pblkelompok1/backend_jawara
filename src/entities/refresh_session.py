import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID

class RefreshSessionModel(Base):
    __tablename__ = 'm_refresh_session'

    refresh_session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    # Relationship
    user = relationship('UserModel', back_populates='refresh_sessions')

    def __repr__(self):
        return f"<RefreshSession(refresh_session_id={self.refresh_session_id}, user_id={self.user_id}, revoked={self.revoked})>"
