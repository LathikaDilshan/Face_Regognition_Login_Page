from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from collections import Counter
from datetime import datetime
from db.database import get_db
from models.login import attend
from models.register import users
from schemas.login import LoginResponse
from core.security import verify_password, verify_position
from core.auth import create_access_token
from services.face_service import FaceRecognitionDB
from services.model import predict_user
import io
from PIL import Image

face_db = FaceRecognitionDB()

router = APIRouter(
    prefix="/login",
    tags=["Login/Attendance"]
)

@router.post("/", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def user_login_attendance(
    username: str = Form(...),
    position: str = Form(...),
    password: str = Form(None),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Verify user exists
    user_exists = db.query(users).filter(users.username == username).first()

    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify position
    if not verify_position(position, user_exists.position):
        raise HTTPException(status_code=401, detail="Incorrect position")

    # Authentication based on provided credentials
    if images is not None and len(images) > 0:
        # Face scan option - ensemble verification
        predictions = []
        
        for img in images:
            content = await img.read()
            pil_image = Image.open(io.BytesIO(content)).convert('RGB')
            embedding = face_db.get_embedding(pil_image)
            
            if embedding is None:
                continue
                
            # 1. Get Top 10 closest classes from ChromaDB
            tmps = face_db.recognise_class([embedding])
            if tmps and tmps[0]:
                tmp = tmps[0]
                # sort classes by their average index (lower index = closer in cosine distance)
                sorted_classes = sorted(tmp.items(), key=lambda item: item[1])
                top_10_classes = [int(cls) for cls, rank in sorted_classes[:10]]
            else:
                top_10_classes = []
                
            # 2. Get Neural Network Prediction
            predicted_user_id, confidence = predict_user(embedding)
            
            # 3. Combine models: The NN prediction must be among the Top 10 closest neighbors in ChromaDB
            if predicted_user_id is not None and predicted_user_id in top_10_classes:
                predictions.append(predicted_user_id)
            elif top_10_classes:
                # Fallback to the closest match in ChromaDB if NN is untrained, missing, or disagrees
                print(f"NN predicted {predicted_user_id} which is not in top 10: {top_10_classes}. Falling back to ChromaDB top match {top_10_classes[0]}.")
                predictions.append(top_10_classes[0])
                
        if not predictions:
            raise HTTPException(status_code=401, detail="Face authentication failed. Could not recognize user or database is empty.")
            
        # KNN-style majority vote from the 7 photos
        counts = Counter(predictions)
        final_predicted_user_id = counts.most_common(1)[0][0]
        
        if final_predicted_user_id != user_exists.id:
            raise HTTPException(status_code=401, detail="Face does not match the username")
            
    elif password is not None:
        # Password option
        if not verify_password(password, user_exists.password):
            raise HTTPException(status_code=401, detail="Incorrect password")
    else:
        raise HTTPException(status_code=400, detail="Must provide either password or face scan")

    now = datetime.now()
    
    # Store attendance log
    new_attendance = attend(
        username=username,
        attend_time=now,
        position=position
    )
    
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    access_token = create_access_token(data={"sub": new_attendance.username, "attend_id": new_attendance.id})
    
    return {"access_token": access_token, "token_type": "bearer", "attendance": new_attendance}
