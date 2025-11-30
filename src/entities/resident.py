from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database.core import Base
from sqlalchemy.dialects.postgresql import UUID
from src.entities.family import FamilyModel
import enum
import uuid

class BloodType(str, enum.Enum):
    a = "a"
    b = "b"          
    ab = "ab"     
    o = "o"

class DomicileStatus(str, enum.Enum):
    active = "active"          
    moved_out = "moved_out"    
    deceased = "deceased"      
    temporary_absent = "temporary_absent"  
    unknown = "unknown"        

class DataStatus(str, enum.Enum):
    approved = "approved"          
    pending = "pending"

class FamilyRole(str, enum.Enum):
    head = "head"             
    spouse = "spouse"         
    child = "child"           
    dependent = "dependent"   
    other = "other"           

class Gender(str, enum.Enum):
    male = "male"             
    female = "female"         


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
    name = Column(String, nullable=False)
    nik = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    place_of_birth = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    is_deceased = Column(Boolean, nullable=False, default=False)
    family_role = Column(String, nullable=False, default=FamilyRole.other.value)
    religion = Column(String, nullable=True)
    domicile_status = Column(String, nullable=False, default=DomicileStatus.active.value)
    status = Column(String, nullable=False, default=DataStatus.approved.value)
    blood_type = Column(String, nullable=True, default=BloodType.o.value)
    profile_img_path = Column(String, nullable=True, default="storage/default/default_profile.png")
    ktp_path = Column(String, nullable=False)
    kk_path = Column(String, nullable=False)
    birth_certificate_path = Column(String, nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    occupation_id = Column(Integer, ForeignKey('m_occupation.occupation_id'), nullable=False)

    user_rel = relationship('UserModel', back_populates='resident_rel', uselist=False)
    family_rel = relationship('FamilyModel', back_populates='residents_rel')
    occupation_rel = relationship('OccupationModel', back_populates='residents')

    def __repr__(self):
        return (
            f"<Resident(resident_id={self.resident_id}, "
            f"name='{self.name}', nik='{self.nik}', phone='{self.phone}', "
            f"family_id={self.family_id}, occupation_id={self.occupation_id})>"
        )
