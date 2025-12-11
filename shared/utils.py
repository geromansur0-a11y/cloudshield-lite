import hashlib
import magic

def compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_file_type(file_path: str) -> str:
    return magic.from_file(file_path, mime=True)

# Daftar hash malware contoh (ganti dengan database sungguhan)
KNOWN_MALWARE_HASHES = {
    "44d88612fea8a8f36de82e1278abb02f88d88612fea8a8f36de82e1278abb02f",  # dummy
  }
