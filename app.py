from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"

# =========================
# DATABASE SETUP (SQLite)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return "<h2>AI Interview Platform Running Successfully 🚀</h2><a href='/register'>Register</a> | <a href='/login'>Login</a>"

# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return """
        <h2>Register</h2>
        <form method="post">
            Name: <input name="name"><br><br>
            Email: <input name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Register</button>
        </form>
    """

# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Login ❌"

    return """
        <h2>Login</h2>
        <form method="post">
            Email: <input name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Login</button>
        </form>
    """

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return f"""
        <h2>Welcome {session['user']} 🎉</h2>
        <p>This is your Dashboard</p>
        <a href="/logout">Logout</a>
    """

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =========================
# RENDER / GUNICORN ENTRY
# =========================
if __name__ == "__main__":
    app.run(debug=True)
