from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID
from src.entities.home import HomeModel
import uuid

class FamilyModel(Base):
    __tablename__ = 'm_family'

    family_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_name = Column(String, nullable=False)
    kk_path = Column(String, nullable=False)
    status = Column(String, nullable=False)
    resident_id = Column(UUID(as_uuid=True), nullable=True)
    rt_id = Column(Integer, ForeignKey('m_rt.rt_id'), nullable=False)

    residents_rel = relationship('ResidentModel', back_populates='family_rel')
    movements_rel = relationship('FamilyMovementModel', back_populates='family_rel')
    homes_rel = relationship('HomeModel', back_populates='family')
    rt_rel = relationship('RTModel', back_populates='families_rel')

    def __repr__(self):
        return f"<FamilyModel(family_id={self.family_id}, family_name={self.family_name}, rt_id={self.rt_id}, status={self.status})>"
    
class FamilyMovementModel(Base):
    __tablename__ = 'm_family_movement'

    family_movement_id = Column(Integer, primary_key=True, autoincrement=True)
    reason = Column(String, nullable=False)
    old_address = Column(String, nullable=False)
    new_address = Column(String, nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    family_rel = relationship('FamilyModel', back_populates='movements_rel')

    def __repr__(self):
        return f"<FamilyMovementModel(family_movement_id={self.family_movement_id}, reason={self.reason}, old_address={self.old_address}, new_address={self.new_address}, family_id={self.family_id})>"


class RTModel(Base):
    __tablename__ = 'm_rt'

    rt_id = Column(Integer, primary_key=True, autoincrement=True)
    rt_name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)

    families_rel = relationship('FamilyModel', back_populates='rt_rel')
    user_rel = relationship('UserModel', back_populates='rt_rel')

    def __repr__(self):
        return f"<RTModel(rt_id={self.rt_id}, rt_name={self.rt_name})>"