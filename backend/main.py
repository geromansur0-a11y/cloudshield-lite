from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import tempfile
import os
import hashlib

# Daftar hash malware contoh (ganti dengan database nyata)
KNOWN_MALWARE_HASHES = {
    "44d88612fea8a8f36de82e1278abb02f88d88612fea8a8f36de82e1278abb02f"
}

def compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

app = FastAPI(title="CloudShield Lite")

# Sajikan file HTML statis
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("../static/index.html") as f:
        return HTMLResponse(f.read())

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
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
            "reason": "Known malware hash" if malicious else "Clean"
        }
    finally:
        os.unlink(tmp_path)  # Hapus segera!
import magic
file_type = magic.from_file(tmp_path, mime=True)
# Lalu kembalikan di response: "file_type": file_type
