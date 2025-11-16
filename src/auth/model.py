from uuid import UUID
from pydantic import BaseModel, EmailStr
from sqlalchemy import String

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str

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
    


