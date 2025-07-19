from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    tel: str | None = None
    address: str | None = None

class UserCreate(User):
    password: str

class UserResponse(User):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    

