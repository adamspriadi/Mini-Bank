# Mini Bank - Aplikasi Web Sederhana (Flask)

### Deskripsi
Aplikasi contoh mini bank sederhana menggunakan Flask dan SQLite.
Fitur:
- Registrasi pengguna
- Login / Logout
- Dashboard menampilkan saldo
- Deposit dan Withdraw sederhana

### Cara menjalankan (lokal)
1. Buat virtual environment (opsional):
   `python -m venv venv`  
   `source venv/bin/activate` (Linux/macOS) atau `venv\Scripts\activate` (Windows)
2. Install dependency:
   `pip install -r requirements.txt`
3. Jalankan:
   `python app.py`
4. Buka http://127.0.0.1:5000 di browser.

**Catatan:** Ganti `app.secret_key` di `app.py` sebelum deploy ke publik.
