from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID
from src.entities.user import UserModel

class FamilyModel(Base):
    __tablename__ = 'm_family'

    family_id = Column(UUID(as_uuid=True), primary_key=True)
    family_name = Column(String, unique=True, nullable=False)
    kk_path = Column(String, unique=True, nullable=False)
    status = Column(String, unique=True, nullable=False)
    rt_id = Column(Integer, ForeignKey('m_rt.rt_id'), nullable=False)

    residents_rel = relationship('ResidentModel', back_populates='family_rel')
    movements_rel = relationship('FamilyMovementModel', back_populates='family_rel')

    def __repr__(self):
        return f"<FamilyModel(family_id={self.family_id}, family_name={self.family_name}, kk_path={self.kk_path}, status={self.status})>"

class FamilyMovementModel(Base):
    __tablename__ = 'm_family_movement'

    family_movement_id = Column(Integer, primary_key=True, autoincrement=True)
    reason = Column(String, unique=True, nullable=False)
    old_address = Column(String, unique=True, nullable=False)
    new_address = Column(String, unique=True, nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    family_rel = relationship('FamilyModel', back_populates='movements_rel')

    def __repr__(self):
        return f"<FamilyMovementModel(family_movement_id={self.family_movement_id}, reason={self.reason}, old_address={self.old_address}, new_address={self.new_address}, family_id={self.family_id})>"