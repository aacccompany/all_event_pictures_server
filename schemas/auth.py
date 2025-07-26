from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    tel: str | None = None
    role: str = "user"
    enabled: bool = True

class UserCreate(User):
    password: str = Field(..., min_length=8, max_length=12, description="Your password must be between 8 and 12 characters long.")

class UserResponse(User):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    

