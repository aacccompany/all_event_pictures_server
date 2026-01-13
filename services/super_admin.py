from sqlalchemy.orm import Session
from schemas.super_admin import UserCreateAdmin, UserUpdateAdmin
from repositories.auth import UserRepository
from utils.auth_utils import hash_password
from fastapi import HTTPException, status

class SuperAdminService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_users(self, page: int, size: int):
        skip = (page - 1) * size
        items, total = self.repo.get_all(skip, size)
        return {"items": items, "total": total, "page": page, "size": size}

    def get_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def create_user(self, user_data: UserCreateAdmin):
        if self.repo.get_by_email(user_data.email):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        # Convert to dict and exclude confirm_password
        user_dict = user_data.model_dump(exclude={'confirm_password'})
        # Hash password
        user_dict['password'] = hash_password(user_dict['password'])
        
        return self.repo.create(user_dict)

    def update_user(self, user_id: int, user_update: UserUpdateAdmin):
        user = self.get_user(user_id)
        # Exclude confirm_password from update data
        update_data = user_update.model_dump(exclude_unset=True, exclude={'confirm_password'})
        
        if "password" in update_data and update_data["password"]:
            update_data["password"] = hash_password(update_data["password"])
        
        return self.repo.update(user, update_data)

    def delete_user(self, user_id: int):
        user = self.repo.delete(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
