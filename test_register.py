import requests
import uuid
import time

data = {
    'fullName': f'Supabase User {uuid.uuid4().hex[:6]}',
    'email': f'supabase-{int(time.time())}@test.com',
    'phoneNumber': '9876543210',
    'address': 'Cloud City',
    'city': 'Internet',
    'zipCode': '99999',
    'password': 'secure123',
    'confirmPassword': 'secure123'
}

print(f"Testing registration with email: {data['email']}")
try:
    response = requests.post('http://localhost:5000/api/register', json=data, timeout=30)
    print(f'Status: {response.status_code}')
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Success! User registered")
        print(f"User ID: {result['user']['id']}")
        print(f"Email: {result['user']['email']}")
    else:
        print(f'Error response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
