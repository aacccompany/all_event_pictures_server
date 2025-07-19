from sqlalchemy.orm import Session
from repositories.user import UserRepository
from schemas.user import UserCreate, User
from fastapi import HTTPException, status
from utils.auth_utils import hash_password, verify_password, create_access_token
from fastapi import Depends, HTTPException


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_user(self, user: UserCreate):
        if self.repo.get_by_email(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        user.password = hash_password(user.password)
        return self.repo.create(user)

    def authenticate_user(self, email: str, password: str):
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    def generate_token(self, user: User):
        return {
            "access_token": create_access_token({"sub": user.email}),
            "token_type": "bearer",
        }

