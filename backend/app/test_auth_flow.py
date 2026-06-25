import httpx
import uuid
import sys

base = 'http://127.0.0.1:8000'
username = f"test_{uuid.uuid4().hex[:8]}"
password = 'TestPass123'

print('Testing auth flow against', base)
with httpx.Client(timeout=10) as client:
    try:
        r = client.post(f"{base}/api/auth/register", json={'username': username, 'password': password})
    except Exception as e:
        print('register request error', e)
        sys.exit(2)
    print('register', r.status_code, r.text)
    if r.status_code != 200:
        sys.exit(1)
    token = r.json().get('token')

    r2 = client.post(f"{base}/api/auth/login", json={'username': username, 'password': password})
    print('login', r2.status_code, r2.text)
    if r2.status_code != 200:
        sys.exit(1)
    token2 = r2.json().get('token')

    headers = {'Authorization': f'Bearer {token2}'}
    r3 = client.get(f"{base}/api/auth/me", headers=headers)
    print('me', r3.status_code, r3.text)

    r4 = client.post(f"{base}/api/auth/logout", json={'token': token2})
    print('logout', r4.status_code, r4.text)

    r5 = client.get(f"{base}/api/auth/me", headers=headers)
    print('me after logout', r5.status_code, r5.text)

print('Done')
