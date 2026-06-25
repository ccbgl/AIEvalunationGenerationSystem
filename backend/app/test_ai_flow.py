import httpx
import uuid

base='http://127.0.0.1:8000'
username = f"ai_{uuid.uuid4().hex[:8]}"
password = 'TestPass123'

with httpx.Client(timeout=10) as c:
    r = c.post(f"{base}/api/auth/register", json={'username': username, 'password': password})
    print('register', r.status_code, r.text)
    token = r.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}

    payload = {'shop_id': 1, 'level': 'recommend', 'tags': ['service','fast'], 'target_platform': 'xiaohongshu'}
    r2 = c.post(f"{base}/api/evaluations/generate_authenticated", json=payload, headers=headers)
    print('generate', r2.status_code, r2.text)
    if r2.status_code==200:
        content = r2.json().get('content')
        remaining = r2.json().get('remaining')
        print('content', content)
        print('remaining', remaining)
        # submit
        payload2 = {**payload, 'content': content, 'is_ai': True}
        r3 = c.post(f"{base}/api/evaluations/", json=payload2, headers=headers)
        print('submit', r3.status_code, r3.text)
    else:
        print('generate failed')
