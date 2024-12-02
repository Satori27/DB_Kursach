from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    organization_name: UUID
    


class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
