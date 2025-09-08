from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_redirect_and_qr():
    # Create
    r = client.post('/api/shorten', json={'long_url': 'https://example.com'})
    assert r.status_code == 200
    data = r.json()
    code = data['code']

    # Meta
    r = client.get(f'/api/{code}')
    assert r.status_code == 200
    meta = r.json()
    assert meta['clicks'] == 0

    # Redirect increments
    r = client.get(f'/{code}', allow_redirects=False)
    assert r.status_code == 307

    r = client.get(f'/api/{code}')
    assert r.status_code == 200
    meta = r.json()
    assert meta['clicks'] == 1
    assert meta['last_clicked'] is not None

    # QR
    r = client.get(f'/qr/{code}.png')
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
