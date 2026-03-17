import os
import torch
import chromadb
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image

class FaceRecognitionDB:
    def __init__(self, collection_name="user_faces", db_path="./chroma_db"):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        # Initialize MTCNN and InceptionResnetV1
        self.mtcnn = MTCNN(image_size=160, margin=0, device=self.device)
        self.vgg = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # creates/opens a collection(table) on database
        self.collection_name = collection_name
        self.db = self.retrieve_collection(self.collection_name)

    def retrieve_collection(self, collection_name):
        return self.client.get_or_create_collection(name=collection_name)

    def collection_exists(self, collection):
        # check whether collection exists
        return collection in [col.name for col in self.client.list_collections()]

    def get_embedding(self, image: Image.Image):
        """
        Extracts face embedding from a PIL Image.
        """
        face = self.mtcnn(image)
        if face is not None:
            face = face.unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.vgg(face)
                return embedding.cpu().numpy().flatten().tolist()
        return None

    def store_user_embeddings(self, user_id: int, embeddings: list):
        """
        Stores multiple embeddings for a single user ID in ChromaDB.
        """
        if not embeddings:
            return
            
        ids = [f"user_{user_id}_img_{i}" for i in range(len(embeddings))]
        metadatas = [{"user_id": user_id, "cls": str(user_id)} for _ in range(len(embeddings))]
        
        self.db.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
