from flask import Flask, render_template, request,redirect
from db import get_db_connection
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sj448371@gmail.com'
app.config['MAIL_PASSWORD'] = 'eoalmniuozcqmamz'
app.config['MAIL_DEFAULT_SENDER'] = 'sj448371@gmail.com'

mail = Mail(app)
serializer = URLSafeTimedSerializer('secret-key')

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


from flask import redirect

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return "Email not registered"

        token = serializer.dumps(email, salt='password-reset')
        reset_link = f"https://lardaceous-oleta-subformative.ngrok-free.dev/reset-password/{token}"

        msg = Message(
            subject="Password Reset Request",
            recipients=[email],
            body=f"""You requested a password reset.

Click the link below to reset your password:
{reset_link}

This link is valid for 10 minutes.
"""
        )

        mail.send(msg)

        return "Reset link sent to your email"

    return render_template('forgot_password.html')
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            salt='password-reset',
            max_age=600
        )
    except:
        return "Reset link expired or invalid"

    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return "Passwords do not match"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (password, email)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('reset_password.html')


if __name__ == "__main__":
    app.run(debug=True)
