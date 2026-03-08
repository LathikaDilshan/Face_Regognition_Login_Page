import urllib.request
import json
import time

def test_register():
    url = "http://localhost:8005/api/register/"
    data = {"username": "testuser", "email": "test@test.com", "position": "dev", "password": "password123"}
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            print("Register Response:", res.read().decode())
    except Exception as e:
        print("Register Error:", e.read().decode() if hasattr(e, 'read') else str(e))

def test_login():
    url = "http://localhost:8005/api/login/"
    data = {"username": "testuser", "position": "dev"}
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            print("Login Response:", res.read().decode())
    except Exception as e:
        print("Login Error:", e.read().decode() if hasattr(e, 'read') else str(e))

if __name__ == "__main__":
    time.sleep(2)  # give server time to ensure it's fully up
    print("Testing APIs...")
    test_register()
    test_login()
