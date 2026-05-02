import requests
import json

data = {
    'fullName': 'Test User',
    'email': 'test@example.com',
    'phoneNumber': '1234567890',
    'address': 'Test Address',
    'city': 'Test City',
    'zipCode': '12345',
    'password': 'password123',
    'confirmPassword': 'password123'
}

try:
    response = requests.post('http://localhost:5000/api/register', json=data, timeout=10)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
