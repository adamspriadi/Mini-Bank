from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bank.db"

app = Flask(__name__)
app.secret_key = "ganti_dengan_rahasia_anda"  # ubah ini sebelum deploy

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.executescript(""" 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 0
    );
    """)
    db.commit()
    db.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Username dan password diperlukan.")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
                       (username, hashed, 0.0))
            db.commit()
            flash("Pendaftaran berhasil. Silakan login.")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Username sudah digunakan.")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Username atau password salah.")
        return redirect(url_for("login"))
    return render_template("login.html")

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    return user

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

@app.route("/deposit", methods=["POST"])
def deposit():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    amount = float(request.form.get("amount", 0))
    if amount <= 0:
        flash("Jumlah harus lebih dari 0.")
        return redirect(url_for("dashboard"))
    db = get_db()
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user["id"]))
    db.commit()
    flash(f"Berhasil deposit Rp{amount:.2f}")
    return redirect(url_for("dashboard"))

@app.route("/withdraw", methods=["POST"])
def withdraw():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    amount = float(request.form.get("amount", 0))
    if amount <= 0:
        flash("Jumlah harus lebih dari 0.")
        return redirect(url_for("dashboard"))
    if user["balance"] < amount:
        flash("Saldo tidak cukup.")
        return redirect(url_for("dashboard"))
    db = get_db()
    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user["id"]))
    db.commit()
    flash(f"Berhasil tarik Rp{amount:.2f}")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
