from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import tempfile
import os
import hashlib

# Daftar hash malware contoh (SHA256)
KNOWN_MALWARE_HASHES = {
    # Contoh hash fiktif — ganti dengan daftar nyata jika mau
    "ff9403ef5c7c69ca"
}

def compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

app = FastAPI(title="CloudShield Lite")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    # Baca file HTML dari folder static
    with open("../static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name  # <-- tmp_path didefinisikan di sini

    try:
        # Hitung hash file
        file_hash = compute_hash(tmp_path)
        # Cek apakah hash dikenal sebagai malware
        malicious = file_hash in KNOWN_MALWARE_HASHES

        return {
            "filename": file.filename,
            "hash": file_hash,
            "malicious": malicious,
            "reason": "Known malware hash" if malicious else "Clean"
        }
    finally:
        # Hapus file sementara — pastikan selalu dihapus!
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
