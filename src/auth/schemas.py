from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlalchemy import String

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "citizen"

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None
    role: str | None = None
    def get_uuid(self) -> UUID | None:
        if self.user_id:
            return UUID(self.user_id)
        return None
    
    def get_role(self) -> String | None:
        if self.role:
            return UUID(self.role)
        return None

class ResidentSubmissionRequest(BaseModel):
    name: str
    nik: str
    phone: str | None = None
    place_of_birth: str
    date_of_birth: str  # ISO format string, e.g. 'YYYY-MM-DD'
    gender: str
    family_role: str
    religion: str | None = None
    domicile_status: str | None = None
    status: str | None = None
    blood_type: str | None = None
    family_id: str
    occupation_id: int

    # File fields handled as UploadFile in endpoint, not in schema



