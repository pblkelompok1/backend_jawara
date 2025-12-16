from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlalchemy import String
from typing import Optional

class ResidentList(BaseModel):
    resident_id: str
    nik: str
    name: str
    phone: Optional[str] = None
    place_of_birth: str
    date_of_birth: str
    gender: str
    is_deceased: bool
    family_role: str
    religion: Optional[str] = None
    domicile_status: str
    status: str
    blood_type: Optional[str] = None
    profile_img_path: Optional[str] = None
    ktp_path: Optional[str] = None
    kk_path: str
    birth_certificate_path: str
    occupation_id: int
    occupation_name: Optional[str] = None
    family_id: str
    
    class Config:
        orm_mode = True  
    
class FamilyListResponse(BaseModel):
    family_id: str
    family_name: str
    head_of_family: Optional[str] = None
    address: Optional[str] = None
    rt_name: str
    
    class Config:
        orm_mode = True

class ResidentsFilter(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    is_deceased: Optional[bool] = None
    domicile_status: Optional[str] = None
    occupation: Optional[str] = None
    family_id: Optional[str] = None
    limit: int = 20
    offset: int = 0



class PendingUserSignUp(BaseModel):
    user_id: str
    email: EmailStr
    role: str
    status: str
    resident_id: Optional[str] = None

    class Config:
        orm_mode = True

class PendingUserSignUpList(BaseModel):
    pending_users: list[PendingUserSignUp]


class ResidentMeUpdate(BaseModel):
    religion: Optional[str] = None
    phone: Optional[str] = None
    blood_type: Optional[str] = None
    occupation_id: Optional[int] = None

class ResidentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    place_of_birth: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    family_role: Optional[str] = None
    religion: Optional[str] = None
    blood_type: Optional[str] = None
    occupation_id: Optional[int] = None


class UserRegistrationItem(BaseModel):
    user_id: str
    email: str
    role: str
    status: str
    name: Optional[str] = None
    nik: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    family_role: Optional[str] = None
    ktp_path: Optional[str] = None
    kk_path: Optional[str] = None
    
    class Config:
        orm_mode = True


class UserListFilter(BaseModel):
    status: Optional[str] = None  # 'pending', 'approved', 'rejected'
    role: Optional[str] = None
    limit: int = 20
    offset: int = 0


class UserListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[UserRegistrationItem]