from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from shared.utils import compute_hash, get_file_type, KNOWN_MALWARE_HASHES

# Mock fungsi AI & sandbox (ganti dengan import sungguhan di produksi)
def predict_malware_prob(path: str) -> float:
    return 0.1  # placeholder

async def run_in_sandbox(path: str) -> dict:
    return {"suspicious": False}

app = FastAPI(title="CloudShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        file_hash = compute_hash(tmp_path)
        file_type = get_file_type(tmp_path)

        if file_hash in KNOWN_MALWARE_HASHES:
            return {"malicious": True, "reason": "Known malware hash"}

        is_executable = file_type in ["application/x-dosexec", "application/x-executable"]
        ai_score = predict_malware_prob(tmp_path) if is_executable else 0.0

        if ai_score > 0.9:
            return {"malicious": True, "reason": "AI: High-risk", "ai_score": ai_score}

        sandbox_result = await run_in_sandbox(tmp_path) if (is_executable and ai_score > 0.5) else None
        if sandbox_result and sandbox_result.get("suspicious"):
            return {"malicious": True, "reason": "Sandbox: Suspicious", "sandbox": sandbox_result}

        return {
            "malicious": False,
            "filename": file.filename,
            "file_type": file_type,
            "hash": file_hash,
            "ai_score": ai_score
        }
    finally:
        os.unlink(tmp_path)
