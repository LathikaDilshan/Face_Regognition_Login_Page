from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

try:
    response = client.post(
        "/api/register/",
        json={"username": "testuser_tc", "email": "tc@test.com", "position": "dev", "password": "password123"}
    )
    print("STATUS:", response.status_code)
    try:
        print("JSON:", response.json())
    except:
        print("TEXT:", response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
