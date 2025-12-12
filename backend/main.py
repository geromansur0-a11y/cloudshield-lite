from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import tempfile
import os
import hashlib
import time

# --- Konfigurasi ---
MALWARE_HASH_FILE = "malware_hashes.txt"
RATE_LIMIT = "5/minute"  # Maks 5 scan per menit per IP

# --- Load daftar hash saat startup ---
def load_malware_hashes():
    if not os.path.exists(MALWARE_HASH_FILE):
        return set()
    with open(MALWARE_HASH_FILE, "r") as f:
        return {line.strip() for line in f if line.strip()}

KNOWN_MALWARE_HASHES = load_malware_hashes()

# --- Inisialisasi FastAPI + Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CloudShield Lite")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def is_dangerous_extension(filename: str) -> bool:
    dangerous = {".exe", ".bat", ".cmd", ".scr", ".pif", ".com", ".dll", ".jar"}
    return any(filename.lower().endswith(ext) for ext in dangerous)

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("../static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/scan")
@limiter.limit(RATE_LIMIT)
async def scan_file(request: Request, file: UploadFile = File(...)):
    # Cek ekstensi berbahaya
    if is_dangerous_extension(file.filename):
        return {
            "filename": file.filename,
            "hash": None,
            "malicious": True,
            "reason": "File executable berpotensi berbahaya",
            "risk": "high"
        }

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        file_hash = compute_hash(tmp_path)
        malicious = file_hash in KNOWN_MALWARE_HASHES

        return {
            "filename": file.filename,
            "hash": file_hash,
            "malicious": malicious,
            "reason": "Known malware hash" if malicious else "Tidak ditemukan ancaman",
            "risk": "critical" if malicious else "low",
            "scan_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
