from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.config import settings
from db.database import get_db
from models.login import attend

# We use HTTPBearer so Swagger UI accepts a pasted token rather than trying to auto-submit form data to the JSON login endpoint.
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        attend_id: int = payload.get("attend_id")
        if username is None or attend_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Verify session is valid (logout_time is None)
    attendance_record = db.query(attend).filter(attend.id == attend_id).first()
    
    if attendance_record is None:
        raise credentials_exception
        
    if attendance_record.logout_time is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (Logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return {"username": username, "attend_id": attend_id}
