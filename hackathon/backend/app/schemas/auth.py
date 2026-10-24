from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr

class Verify2FARequest(BaseModel):
    email: EmailStr
    code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"