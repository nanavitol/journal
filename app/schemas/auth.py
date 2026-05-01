from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[int] = None
    login: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    login: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str