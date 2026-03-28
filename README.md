# Face Recognition Login System

## Description
This project is an advanced, secure authentication system that leverages facial recognition technology to provide a frictionless login experience. It replaces or supplements standard text-based login mechanisms with a computer-vision pipeline, allowing users to register and sign in to their accounts using their physical appearance as a primary credential.

## Frontend Technologies
*   **React (v19)**: Core library used for building the interface components.
*   **Vite**: Fast frontend build tool and development server.
*   **React Router DOM**: Utilized for client-side routing and managing application navigation (e.g., moving between Registration, Login, and secure Home pages).
*   **Web API (MediaDevices)**: Interacts with the user's webcam natively in the browser to capture real-time photo samples.

## Backend Technologies
*   **Python**: Primary language used for the backend logic and ML orchestration.
*   **FastAPI**: High-performance backend framework used to create robust RESTful API endpoints.
*   **ChromaDB**: An advanced vector database used to store, manage, and retrieve high-dimensional facial embeddings efficiently.
*   **MTCNN (Multi-task Cascaded Convolutional Networks)**: Deep learning model used to detect the location of a face within the captured images and crop it.
*   **InceptionResnetV1**: Pre-trained convolutional neural network used to transform the cropped face into a 512-dimensional vector embedding.
*   **K-Nearest Neighbors (KNN)**: Classification algorithm applied to vector similarities to predict the user identity.

## Model Workflow

### When a New User Registers
1.  **Face Capture**: The frontend application activates the webcam and captures a set of baseline images (e.g., 7 photos) of the new user.
2.  **Image Processing**: The images are sent to the FastAPI backend, where **MTCNN** is executed to detect and consistently crop the face out of the background.
3.  **Embedding Generation**: Each cropped face is passed through the **InceptionResnetV1** model. This converts the visual data of the facial features into a secure vector (embedding).
4.  **Vector Storage**: The generated face embeddings are associated with the user's unique identity and safely inserted into **ChromaDB**. Any traditional credentials (like email and password) are stored in the core database.

### When a User Comes to Log In
1.  **Live Capture**: The user points their camera at themselves on the login screen, and the frontend captures a fresh set of sample photos.
2.  **Real-Time Processing**: The backend temporarily extracts the embeddings from these live attempt photos using the same **MTCNN** and **InceptionResnetV1** pipeline.
3.  **Database Querying**: The backend uses **ChromaDB's** vector query engine to compute the distance between the newly generated embeddings and the embeddings stored during registration.
4.  **Matching & Verification**: A **K-Nearest Neighbors (KNN)** approach groups the closest matches. If the live embeddings tightly cluster with a specific registered user's embeddings beyond a designated confidence threshold, the prediction model validates the identity.
5.  **Access Granted**: Upon a successful positive match, the user is authenticated.

## Security Features

*   **Password Hashing**: User passwords are encrypted using secure cryptographic hashing algorithms before being stored. Plain text passwords are never kept in the database, rendering them safe from potential data breaches.
*   **Storing Face Embeddings, Not Raw Images**: The system significantly prioritizes user privacy; raw photographs from the webcam are not persistently stored. The database only retains the mathematical vector embeddings. It is computationally infeasible for a malicious actor to reverse-engineer these embeddings back into a real photograph of the user.
*   **JWT Token Issuance**: Once facial verification is successful, the server issues a digitally signed **JSON Web Token (JWT)**. The frontend stores this token and includes it in the header of subsequent API requests to access protected routes securely. This ensures stateless and tamper-proof session management across the application without unnecessarily querying credentials repeatedly.
