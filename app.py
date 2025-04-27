from flask import Flask, render_template, request, redirect, session
import sqlite3
from sentiments import second
import os

app = Flask(__name__)
# initializing the user cookie
app.secret_key = os.urandom(24)
# blueprint to call the second python file in the project.
app.register_blueprint(second)

# SQLite database configuration
DATABASE = 'user_database.db'

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    """Initialize the database with the users table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# call the login template when the url is http://localhost:5000/
@app.route('/')
def login():
    return render_template('login.html')

# call the register template when the url is http://localhost:5000/register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Using parameterized queries for security (prevents SQL injection)
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    
    # check if a user has already logged in
    if user:
        session['user_id'] = user['id']
        return redirect('/home')
    else:
        return redirect('/')

@app.route('/add_user', methods=['POST'])
def add_user():
    # get user login data and pass the data to database
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Using parameterized queries for security
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                      (name, email, password))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        session['user_id'] = user['id']
        
        return redirect('/home')
    except sqlite3.IntegrityError:
        # This happens if the email already exists (due to UNIQUE constraint)
        return "Email already registered. Please use a different email."
    finally:
        conn.close()

@app.route('/logout')
def logout():
    # close the session
    session.pop('user_id', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)