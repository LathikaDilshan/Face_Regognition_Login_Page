from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from models.login import attend
from core.auth import get_current_user

router = APIRouter(
    prefix="/logout",
    tags=["Logout"]
)

@router.post("/", status_code=status.HTTP_200_OK)
def logout(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # The get_current_user dependency already ensures the user is valid and not logged out
    attend_id = current_user.get("attend_id")
    
    attendance_record = db.query(attend).filter(attend.id == attend_id).first()
    if not attendance_record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
        
    # Explicitly set logout time to the current time to invalidate future session access
    attendance_record.logout_time = datetime.now()
    db.commit()
    
    return {"message": "Successfully logged out"}
