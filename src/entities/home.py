from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID

class HomeModel(Base):
    __tablename__ = 'm_home'

    home_id = Column(Integer, primary_key=True, autoincrement=True)
    home_name = Column(String, nullable=False)
    home_address = Column(String, nullable=False)
    status = Column(String, nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    family = relationship('FamilyModel', back_populates='homes_rel')


    histories = relationship('HomeHistoryModel', back_populates='home_rel')

    def __repr__(self):
        return f"<HomeModel(home_id={self.home_id}, home_name={self.home_name}, home_address={self.home_address}, status={self.status})>"

class HomeHistoryModel(Base):
    __tablename__ = 't_home_history'

    home_id = Column(Integer, ForeignKey('m_home.home_id'), primary_key=True)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), primary_key=True)
    moved_in_date = Column(Date, nullable=False)
    moved_out_date = Column(Date, nullable=True)

    home_rel = relationship('HomeModel', back_populates='histories')

    def __repr__(self):
        return f"<HomeHistoryModel(home_id={self.home_id}, family_id={self.family_id}, moved_in_date={self.moved_in_date}, moved_out_date={self.moved_out_date})>"
