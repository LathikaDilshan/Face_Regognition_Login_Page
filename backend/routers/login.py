from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import get_db
from models.login import attend
from models.register import users
from schemas.login import AttendCreate, AttendOut

router = APIRouter(
    prefix="/login",
    tags=["Login/Attendance"]
)

@router.post("/", response_model=AttendOut, status_code=status.HTTP_200_OK)
def user_login_attendance(attend_in: AttendCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user_exists = db.query(users).filter(users.username == attend_in.username).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now()
    
    # Store attendance log
    new_attendance = attend(
        username=attend_in.username,
        attend_date=now.date(),
        attend_time=now,
        position=attend_in.position
    )
    
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    return new_attendance
