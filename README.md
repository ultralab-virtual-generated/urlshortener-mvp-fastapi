# Minimal URL Shortener (MVP)

A simple, safe, containerized URL shortener with click analytics and QR codes.

Tech stack: Python 3.11, FastAPI, Uvicorn, SQLite (SQLAlchemy), qrcode (Pillow).

Endpoints:
- POST /api/shorten {"long_url": "https://example.com"} -> {code, short_url, long_url}
- GET /{code} -> 307 redirect to long_url (increments clicks, updates last_clicked)
- GET /api/{code} -> metadata (clicks, timestamps)
- GET /qr/{code}.png -> QR code PNG of the short URL
- GET / -> tiny HTML form to create links

Run locally:
- make install
- make run (defaults to port 8000)

Docker:
- make docker-build
- make docker-run

Testing:
- make test

License: MIT
