# CloudShield Lite

Antivirus cloud ringan, multiplatform, fokus pada browser HP.

## Jalankan

1. Install Docker
2. Salin semua file ke folder
3. Jalankan:
   ```bash
   docker-compose up --build

# CARA MENJALANKAN DI TERMUX ANDROID
#####################################
# 1. Update & instal
pkg install python -y
pip install fastapi uvicorn python-multipart slowapi

# 2. Simpan semua file sesuai struktur

# 3. Jalankan
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# AKSES DI CHROME HP
http://127.0.0.1:8000


## ANTI VIRUS INI SANGAT SEDERHANA SILAHKAN KEMBANGKAN LEBIH LANJUT ##
