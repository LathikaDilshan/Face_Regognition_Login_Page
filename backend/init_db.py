import os
import kagglehub
import glob
from PIL import Image
from services.face_service import FaceRecognitionDB
import sys

# Change directory context if needed or run from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    print("Downloading dataset...")
    path = kagglehub.dataset_download("vishesh1412/celebrity-face-image-dataset")
    print(f"Dataset downloaded to: {path}")

    face_db = FaceRecognitionDB()
    
    # Iterate through folders and extract embeddings
    celebrity_folders = glob.glob(os.path.join(path, "Celebrity Faces Dataset", "*"))
    
    extracted_users = 0
    
    # For dummy initialization, let's assign a user ID based on index
    for user_id, folder_path in enumerate(celebrity_folders, start=1):
        user_name = os.path.basename(folder_path)
        print(f"Processing images for {user_name} (ID: {user_id})...")
        
        image_files = glob.glob(os.path.join(folder_path, "*.jpg")) + glob.glob(os.path.join(folder_path, "*.jpeg"))
        
        embeddings = []
        for img_path in image_files:
            try:
                image = Image.open(img_path).convert('RGB')
                embedding = face_db.get_embedding(image)
                if embedding is not None:
                    embeddings.append(embedding)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                
        if embeddings:
            face_db.store_user_embeddings(user_id=user_id, embeddings=embeddings)
            print(f"Stored {len(embeddings)} embeddings for {user_name}.")
            extracted_users += 1
        else:
            print(f"No valid faces found for {user_name}.")
            
    print(f"Database initialization complete. Processed {extracted_users} users.")

if __name__ == "__main__":
    initialize_database()
