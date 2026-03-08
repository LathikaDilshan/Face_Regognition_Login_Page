from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.register import users
from schemas.register import UserCreate, UserOut
from core.security import verify_password

router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(users).filter(users.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    existing_email = db.query(users).filter(users.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = verify_password(user.password , )

    # Create new user record
    new_user = users(
        username=user.username,
        email=user.email,
        position=user.position,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
