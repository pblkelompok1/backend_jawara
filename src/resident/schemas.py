from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlalchemy import String
from typing import Optional

class ResidentList(BaseModel):
    name: str
    phone: str
    email: str
    date_of_birth: str
    gender: str
    is_deceased: bool
    profile_image_url: str
    family_name: str
    religion: str
    occupation: str
    domicile_status: str
    
    class Config:
        orm_mode = True  
    
class ResidentsFilter(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    is_deceased: Optional[bool] = None
    domicile_status: Optional[str] = None
    occupation: Optional[str] = None
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