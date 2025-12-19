import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime


class ReportCategory(str, enum.Enum):
    keamanan = "keamanan"
    kebersihan = "kebersihan"
    infrastruktur = "infrastruktur"
    sosial = "sosial"
    lainnya = "lainnya"


class ReportStatus(str, enum.Enum):
    unsolved = "unsolved"
    inprogress = "inprogress"
    solved = "solved"


class ReportModel(Base):
    __tablename__ = 'm_report'

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False, default="lainnya")
    report_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    status = Column(String, nullable=False, default="unsolved")
    evidence = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ReportModel(id={self.report_id}, name='{self.report_name}', status='{self.status}')>"
