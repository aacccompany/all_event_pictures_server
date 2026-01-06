from pydantic import BaseModel, EmailStr, Field


class SearchEmail(BaseModel):
    email: str


class User(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    tel: str | None = None
    role: str = "user"
    enabled: bool = True
    book_bank_image: str | None = None


class UserCreate(User):
    password: str = Field(
        ...,
        min_length=8,
        max_length=16,
        description="Your password must be between 8 and 16 characters long.",
    )


class UserCreatePhotographer(UserCreate):
    book_bank_image: str = Field(..., description="Book bank image is required for photographers")


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
    payload: UserResponse
