import os
import json
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, confusion_matrix
import torch.optim as optim
from services.face_service import FaceRecognitionDB

class FaceDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.embeddings = torch.tensor(embeddings, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)
        
    def __len__(self):
        return len(self.labels)
        
    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]

class ClassificationModel(nn.Module):
    def __init__(self, num_of_classes):
        super(ClassificationModel, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(512, 64),
            nn.ReLU(),
            nn.Linear(64, num_of_classes)
        )
        self.num_of_classes = num_of_classes

    def forward(self, x):
        return self.classifier(x)

    def saveModel(self, model_name="face_model"):
        model_dir = "saved_models"
        model_path = os.path.join(model_dir, f"{model_name}.pth")
        os.makedirs(model_dir, exist_ok=True)
        torch.save(self.state_dict(), model_path)
        print(f"Model saved at {model_path}")

    def trainModel(self, dataset, epochs=100, lr=0.001, batch_size=32):
        # Ensure batch_size is not larger than dataset
        batch_size = min(batch_size, len(dataset))
        if batch_size == 0:
            print("No data to train on.")
            return

        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)
        
        history = {'x': [], 'y': []}

        for epoch in range(epochs):
            self.train()
            total_loss = 0

            for batch_embeddings, batch_labels in dataloader:
                outputs = self(batch_embeddings)
                loss = criterion(outputs, batch_labels)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)
            history['x'].append(epoch+1)
            history['y'].append(avg_loss)
            
            if (epoch + 1) % 20 == 0 or epoch == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")
        return history

    def evalModel(self, dataset, batch_size=32):
        self.eval()
        all_preds = []
        all_labels = []
        batch_size = min(batch_size, len(dataset))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        with torch.no_grad():
            for inputs, labels in dataloader:
                outputs = self(inputs)
                preds = torch.argmax(outputs, dim=1)
                all_preds.extend(preds.numpy())
                all_labels.extend(labels.numpy())

        acc = accuracy_score(all_labels, all_preds)
        cm = confusion_matrix(all_labels, all_preds)
        return {'accuracy': acc * 100, 'confusion_matrix': cm}

    def loadModel(self, model_name="face_model"):
        model_path = f'saved_models/{model_name}.pth'
        if os.path.exists(model_path):
            self.load_state_dict(torch.load(model_path))
            print("Model loaded successfully.")
            return True
        else:
            print(f"Model file not found at: {model_path}")
            return False

    def inference(self, embedding):
        self.eval()
        # Ensure embedding is a tensor of right shape (1, 512)
        if not isinstance(embedding, torch.Tensor):
            embedding = torch.tensor(embedding, dtype=torch.float32)
        if embedding.dim() == 1:
            embedding = embedding.unsqueeze(0)
            
        with torch.no_grad():
            logits = self(embedding)
            pred_class = torch.argmax(logits, dim=1)
            # also return confidence
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            confidence = probabilities[0][pred_class[0].item()].item()
            return pred_class.tolist()[0], confidence

def retrain_model():
    """Fetches all embeddings from ChromaDB, trains the model, and saves it."""
    try:
        face_db = FaceRecognitionDB()
        collection = face_db.db
        
        # Get all records from ChromaDB
        data = collection.get(include=['embeddings', 'metadatas'])
        
        if not data or not data['embeddings']:
            print("No embeddings found in ChromaDB to train the model.")
            return False
            
        embeddings = data['embeddings']
        metadatas = data['metadatas']
        
        # We need to map actual user_ids (which could be sparse) to 0-indexed classes
        unique_user_ids = sorted(list(set([m['user_id'] for m in metadatas])))
        class_mapping = {user_id: idx for idx, user_id in enumerate(unique_user_ids)}
        idx_to_user = {idx: user_id for idx, user_id in enumerate(unique_user_ids)}
        
        # Save mapping
        mapping_dir = "saved_models"
        os.makedirs(mapping_dir, exist_ok=True)
        with open(os.path.join(mapping_dir, "class_mapping.json"), "w") as f:
            json.dump(idx_to_user, f)
            
        labels = [class_mapping[m['user_id']] for m in metadatas]
        
        dataset = FaceDataset(embeddings, labels)
        
        num_classes = len(unique_user_ids)
        model = ClassificationModel(num_classes)
        
        print(f"Training model with {len(embeddings)} samples across {num_classes} classes...")
        model.trainModel(dataset, epochs=100)
        model.saveModel()
        return True
    except Exception as e:
        print(f"Error during model retraining: {e}")
        return False

def predict_user(embedding):
    """Predicts a user_id from an embedding."""
    try:
        mapping_path = os.path.join("saved_models", "class_mapping.json")
        if not os.path.exists(mapping_path):
            print("Class mapping not found.")
            return None, 0.0
            
        with open(mapping_path, "r") as f:
            idx_to_user = json.load(f)
            
        num_classes = len(idx_to_user)
        model = ClassificationModel(num_classes)
        
        if not model.loadModel():
            return None, 0.0
            
        pred_idx, confidence = model.inference(embedding)
        
        # pred_idx is string in JSON keys, convert mapping accordingly
        user_id = int(idx_to_user[str(pred_idx)])
        return user_id, confidence
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None, 0.0
