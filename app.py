from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "luvia_secure_admin_key"

ADMIN_PASSWORD = "luvia2026"

def init_db():
    conn = sqlite3.connect('luvia_ledger.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            category TEXT,
            amount REAL,
            note TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database immediately when the app boots up on Render
init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "Incorrect password"
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Luvia Admin Login</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-900 text-white flex items-center justify-center h-screen">
            <div class="bg-gray-800 p-8 rounded-xl shadow-lg w-80">
                <h2 class="text-2xl font-bold mb-6 text-center text-amber-400">Luvia Admin</h2>
                ''' + (f'<p class="text-red-400 text-sm mb-4">{error}</p>' if error else '') + '''
                <form method="POST">
                    <input type="password" name="password" placeholder="Enter Password" class="w-full p-3 rounded bg-gray-700 text-white mb-4 border border-gray-600 focus:outline-none focus:border-amber-400" required>
                    <button type="submit" class="w-full bg-amber-500 text-gray-900 font-bold p-3 rounded hover:bg-amber-400 transition">Login</button>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('luvia_ledger.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        entry_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        note = request.form['note']
        
        cursor.execute("INSERT INTO entries (type, category, amount, note) VALUES (?, ?, ?, ?)",
                       (entry_type, category, amount, note))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT type, category, amount, note, date FROM entries ORDER BY id DESC LIMIT 20")
    entries = cursor.fetchall()
    
    cursor.execute("SELECT SUM(amount) FROM entries WHERE type='Sale'")
    total_sales = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount) FROM entries WHERE type='Expense'")
    total_expenses = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return render_template('index.html', entries=entries, total_sales=total_sales, total_expenses=total_expenses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
