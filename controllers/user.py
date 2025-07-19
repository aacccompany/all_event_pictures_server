from fastapi import APIRouter, Depends
from schemas.user import UserResponse, UserCreate,Token, UserLogin
from sqlalchemy.orm import Session
from core.database import get_db
from services.user import UserService


router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def signup(user:UserCreate, db: Session = Depends(get_db)):
    return UserService(db).register_user(user)

@router.post("/login", response_model=Token)
async def signin(user:UserLogin, db:Session = Depends(get_db)):
    user =  UserService(db).authenticate_user(user.email, user.password)
    return UserService(db).generate_token(user)