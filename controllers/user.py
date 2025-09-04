from fastapi import APIRouter, Depends
from schemas.auth import UserResponse, UserCreate,Token, UserLogin
from schemas.event import EventResponse
from sqlalchemy.orm import Session
from core.database import get_db
from services.auth import UserService
from typing import Annotated
from middleware.auth import get_current_user,get_current_admin, get_current_super_admin
from schemas.auth import SearchEmail

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def signup(user:UserCreate, db: Session = Depends(get_db)):
    return UserService(db).register_user(user)

@router.post("/register/user_public", response_model=UserResponse)
async def signup(user:UserCreate, db: Session = Depends(get_db)):
    user.role = "user-public"
    return UserService(db).register_user(user)

@router.post("/login", response_model=Token)
async def signin(user:UserLogin, db:Session = Depends(get_db)):
    user =  UserService(db).authenticate_user(user.email, user.password)
    return UserService(db).generate_token(user)

@router.post("/current-user", response_model=UserResponse)
async def currentUser(user:Annotated[UserResponse, Depends(get_current_user)], db:Session = Depends(get_db)):
    return UserService(db).currentUser(user.email)

@router.post("/current-admin", response_model=UserResponse)
async def currentAdmin(user:Annotated[UserResponse, Depends(get_current_admin)], db:Session = Depends(get_db)):
    return UserService(db).currentAdmin(user.email)

@router.post("/current-superAdmin", response_model=UserResponse)
async def currentSuperAdmin(user:Annotated[UserResponse, Depends(get_current_super_admin)], db:Session = Depends(get_db)):
    return UserService(db).currentSuperAdmin(user.email)

@router.get("/my-events", response_model=list[EventResponse])
async def get_events_by_user(user:Annotated[UserResponse, Depends(get_current_admin)], db:Session = Depends(get_db)):
    return UserService(db).get_events_by_user(user)

@router.get("/events-joined", response_model=list[EventResponse])
async def get_events_by_joined(user:Annotated[UserResponse, Depends(get_current_user)], db:Session = Depends(get_db)):
    return UserService(db).get_events_by_joined(user.id)

@router.get("/user/emails", response_model=list[UserResponse])
async def search_emails(email:SearchEmail, _:Annotated[UserResponse, Depends(get_current_admin)], db:Session = Depends(get_db)):
    return UserService(db).search_emails(email.email)