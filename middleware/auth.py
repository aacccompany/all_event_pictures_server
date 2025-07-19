from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from core.database import get_db
from utils.auth_utils import decode_access_token
from repositories.user import UserRepository

async def get_current_user(request:Request, db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer"):
            raise credentials_exception
        
        token = auth_header.split(" ")[1]
        payload = await decode_access_token(token)
        if not payload or "sub" not in payload:
            raise credentials_exception
        
        email = payload.get("sub")
        user = UserRepository(db).get_by_email(email)
        if user is None:
            raise credentials_exception
        return user
       
    
async def get_current_admin(user = Depends(get_current_user)):
        if user.role not in ["admin", "super-admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this resource")
        return user
    
async def get_current_super_admin(user = Depends(get_current_user)):
        if user.role != "super-admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super-admins are allowed to access this resource")
        return user
