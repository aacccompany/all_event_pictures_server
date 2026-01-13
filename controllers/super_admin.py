from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from core.database import get_db
from middleware.auth import get_current_admin
from schemas.auth import UserResponse
from schemas.super_admin import UserListResponse, UserCreateAdmin, UserUpdateAdmin, UserResponseAdmin
from services.super_admin import SuperAdminService
from typing import Annotated

router = APIRouter(
    prefix="/super-admin/users",
    tags=["Super Admin User Management"],
    dependencies=[Depends(get_current_admin)] 
)

@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return SuperAdminService(db).get_users(page, size)

@router.get("/{id}", response_model=UserResponseAdmin)
async def get_user(
    id: int = Path(..., title="The ID of the user to get"),
    db: Session = Depends(get_db)
):
    return SuperAdminService(db).get_user(id)

@router.post("", response_model=UserResponseAdmin)
async def create_user(
    user: UserCreateAdmin,
    db: Session = Depends(get_db)
):
    return SuperAdminService(db).create_user(user)

@router.put("/{id}", response_model=UserResponseAdmin)
async def update_user(
    user_update: UserUpdateAdmin,
    id: int = Path(..., title="The ID of the user to update"),
    db: Session = Depends(get_db)
):
    return SuperAdminService(db).update_user(id, user_update)

@router.delete("/{id}", response_model=UserResponseAdmin)
async def delete_user(
    id: int = Path(..., title="The ID of the user to delete"),
    db: Session = Depends(get_db)
):
    return SuperAdminService(db).delete_user(id)
