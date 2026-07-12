from pydantic import BaseModel, EmailStr

from models.roles import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: Role
    is_active: bool


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role = Role.PATIENT
