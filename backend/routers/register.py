from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db
from models.register import users
from schemas.register import UserCreate, UserOut
from core.security import get_password_hash
from typing import List
from services.face_service import FaceRecognitionDB
from services.model import retrain_model
import io
from PIL import Image

# Initialize the face recognition database single instance
face_db = FaceRecognitionDB()

router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    background_tasks: BackgroundTasks,
    username: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    password: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Check if username or email already exists
    existing_user = db.query(users).filter(users.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    existing_email = db.query(users).filter(users.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(images) < 15:
        raise HTTPException(status_code=400, detail="Please provide at least 15 face images")

    # Hash the password
    hashed_password = get_password_hash(password)

    # Create new user record
    new_user = users(
        username=username,
        email=email,
        position=position,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Process images for face embeddings
    try:
        embeddings = []
        for upload_file in images:
            content = await upload_file.read()
            image = Image.open(io.BytesIO(content)).convert('RGB')
            embedding = face_db.get_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)

        if embeddings:
            face_db.store_user_embeddings(user_id=new_user.id, embeddings=embeddings)
            background_tasks.add_task(retrain_model)
        else:
            print("Warning: No faces detected in the provided images for user", new_user.username)
    except Exception as e:
        print(f"Error processing images: {e}")
        # Could decide to rollback user creation here or just log the error depending on requirements
        pass
    
    return new_user
