import enum
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID


class ActivityStatus(str, enum.Enum):
    akan_datang = "akan_datang"
    ongoing = "ongoing"
    selesai = "selesai"


class ActivityCategory(str, enum.Enum):
    sosial = "sosial"
    keagamaan = "keagamaan"
    olahraga = "olahraga"
    pendidikan = "pendidikan"
    lainnya = "lainnya"


class ActivityModel(Base):
    __tablename__ = 'm_activity'

    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    status = Column(String, nullable=False, default='akan_datang')
    banner_img = Column(String, nullable=True, default='storage/banner/1.png')
    preview_images = Column(ARRAY(String), nullable=True, default=[])
    category = Column(String, nullable=False, default='lainnya')

    # Relationships
    dashboard_banners = relationship('DashboardBannerModel', back_populates='activity')

    def __repr__(self):
        return f"<ActivityModel(activity_id={self.activity_id}, activity_name='{self.activity_name}', status='{self.status}')>"


class DashboardBannerModel(Base):
    __tablename__ = 't_dashboard_banner'

    banner_id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer, nullable=False)
    activity_id = Column(UUID(as_uuid=True), ForeignKey('m_activity.activity_id'), nullable=False)

    # Relationships
    activity = relationship('ActivityModel', back_populates='dashboard_banners')

    def __repr__(self):
        return f"<DashboardBannerModel(banner_id={self.banner_id}, position={self.position}, activity_id={self.activity_id})>"
