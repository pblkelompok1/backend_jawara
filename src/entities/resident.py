from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.core import Base
from sqlalchemy.dialects.postgresql import UUID
import enum

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

    resident_id = Column(UUID(as_uuid=True), primary_key=True)
    nik = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    place_of_birth = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    is_deceased = Column(Boolean, nullable=False, default=False)
    family_role = Column(String, nullable=False, default=FamilyRole.other.value)
    religion = Column(String, nullable=False)
    domicile_status = Column(String, nullable=False, default=DomicileStatus.active.value)
    blood_type = Column(String, nullable=False, default=BloodType.o.value)
    occupation = Column(String, nullable=False)
    profile_img_path = Column(String, nullable=False, default="default_profile.png")
    ktp_path = Column(String, nullable=False, default="default_profile.png")

    user_id = Column(UUID(as_uuid=True), ForeignKey('m_user.user_id'), nullable=False)
    occupation_id = Column(Integer, ForeignKey('m_occupation.occupation_id'), nullable=False)
    family_id = Column(UUID(as_uuid=True), ForeignKey('m_family.family_id'), nullable=False)

    family = relationship('FamilyModel', back_populates='residents_rel')
    occupation_rel = relationship('OccupationModel', back_populates='residents_rel')

    def __repr__(self):
        return f"<ResidentModel(resident_id={self.resident_id}, nik={self.nik}, phone={self.phone}, family_id={self.family_id})>"
