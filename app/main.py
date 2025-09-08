from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import io
import qrcode

from .models.db import SessionLocal, init_db
from .models.url import URL
from .utils.base62 import generate_code

app = FastAPI(title="Minimal URL Shortener")

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Static placeholder (unused but kept for extensibility)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return (
        """
        <html><head><title>URL Shortener</title></head><body>
        <h1>Shorten a URL</h1>
        <form id=frm>
            <input type=url name=long_url placeholder="https://example.com" style="width:400px" required>
            <button type=submit>Shorten</button>
        </form>
        <pre id=out></pre>
        <script>
        const frm = document.getElementById('frm');
        frm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = new FormData(frm);
            const payload = { long_url: data.get('long_url') };
            const res = await fetch('/api/shorten', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            document.getElementById('out').textContent = await res.text();
        });
        </script>
        </body></html>
        """
    )


@app.post("/api/shorten")
def create_short(body: dict, request: Request):
    long_url = body.get("long_url")
    if not long_url or not isinstance(long_url, str):
        raise HTTPException(status_code=400, detail="long_url is required")

    db: Session = SessionLocal()
    try:
        # Try up to few times to avoid collisions
        for _ in range(5):
            code = generate_code(6)
            url = URL(code=code, long_url=long_url)
            db.add(url)
            try:
                db.commit()
                db.refresh(url)
                break
            except IntegrityError:
                db.rollback()
                continue
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique code")

        short_url = str(request.url_for("redirect_code", code=url.code))
        return {"code": url.code, "short_url": short_url, "long_url": url.long_url}
    finally:
        db.close()


@app.get("/{code}")
def redirect_code(code: str):
    db: Session = SessionLocal()
    try:
        url = db.get(URL, code)
        if not url:
            raise HTTPException(status_code=404, detail="Not found")
        url.clicks = (url.clicks or 0) + 1
        url.last_clicked = datetime.utcnow()
        db.add(url)
        db.commit()
        return RedirectResponse(url.long_url, status_code=307)
    finally:
        db.close()


@app.get("/api/{code}")
def get_meta(code: str, request: Request):
    db: Session = SessionLocal()
    try:
        url = db.get(URL, code)
        if not url:
            raise HTTPException(status_code=404, detail="Not found")
        short_url = str(request.url_for("redirect_code", code=url.code))
        return {
            "code": url.code,
            "long_url": url.long_url,
            "short_url": short_url,
            "clicks": url.clicks,
            "last_clicked": url.last_clicked.isoformat() if url.last_clicked else None,
            "created_at": url.created_at.isoformat() if url.created_at else None,
        }
    finally:
        db.close()


@app.get("/qr/{code}.png")
def qr_png(code: str, request: Request):
    db: Session = SessionLocal()
    try:
        url = db.get(URL, code)
        if not url:
            raise HTTPException(status_code=404, detail="Not found")
        short_url = str(request.url_for("redirect_code", code=url.code))
        img = qrcode.make(short_url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    finally:
        db.close()
