import enum
import uuid
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID

class Gender(str, enum.Enum):
    male = "male"
    female = "female"

class FamilyRole(str, enum.Enum):
    head = "head"
    wife = "wife"
    child = "child"
    other = "other"

class DomicileStatus(str, enum.Enum):
    resident = "resident"
    non_resident = "non_resident"

class ResidentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class BloodType(str, enum.Enum):
    a = "a"
    b = "b"          
    ab = "ab"     
    o = "o"

class OccupationModel(Base):
    __tablename__ = 'm_occupation'

    occupation_id = Column(Integer, primary_key=True, autoincrement=True)
    occupation_name = Column(String, unique=True, nullable=False)

    residents = relationship('ResidentModel', back_populates='occupation_rel')

    def __repr__(self):
        return f"<OccupationModel(occupation_id={self.occupation_id}, occupation_name={self.occupation_name})>"


class ResidentModel(Base):
    __tablename__ = 'm_resident'

    resident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nik = Column(String(16), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(15), nullable=True)
    place_of_birth = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    is_deceased = Column(Boolean, default=False, nullable=False)
    family_role = Column(String(20), nullable=False)
    religion = Column(String(50), nullable=True)
    domicile_status = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default='approved')
    blood_type = Column(String(5), nullable=True)
    profile_img_path = Column(String(255), nullable=True, default='storage/default/default_profile.png')
    ktp_path = Column(String(255), nullable=True)
    kk_path = Column(String(255), nullable=False)
    birth_certificate_path = Column(String(255), nullable=False)
    occupation_id = Column(Integer, ForeignKey('m_occupation.occupation_id'), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    # Relationships
    family_rel = relationship('FamilyModel', back_populates='residents_rel')
    occupation_rel = relationship('OccupationModel', back_populates='residents')
    user = relationship('UserModel', back_populates='resident', foreign_keys='UserModel.resident_id', uselist=False)

    def __repr__(self):
        return f"<Resident(resident_id={self.resident_id}, nik='{self.nik}', name='{self.name}', status='{self.status}')>"
