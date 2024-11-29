from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    


class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
