from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    tel: str | None = None
    address: str | None = None

class UserCreate(User):
    password: str

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
    

