from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime
from schemas.auth import User

class UserCreateAdmin(BaseModel):
    email: EmailStr
    password: str 
    confirm_password: str
    first_name: str | None = None
    last_name: str | None = None
    tel: str | None = None
    role: str = "user"
    enabled: bool = True
    book_bank_image: str | None = None

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreateAdmin':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class UserUpdateAdmin(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    tel: str | None = None
    address: str | None = None
    role: str | None = None
    enabled: bool | None = None
    book_bank_image: str | None = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserUpdateAdmin':
        if self.password and self.confirm_password and self.password != self.confirm_password:
             raise ValueError('Passwords do not match')
        if self.password and not self.confirm_password:
             raise ValueError('Confirm password is required when setting password')
        return self

class UserResponseAdmin(User):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    items: list[UserResponseAdmin]
    total: int
    page: int
    size: int
