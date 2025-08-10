from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "bookreview_secret_2025"
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            book_title TEXT NOT NULL,
            review TEXT NOT NULL
        )
    ''')
    db.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/xss/reflected', methods=['GET', 'POST'])
def xss_reflected():
    username = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        # Reflected XSS üçün sanitize yoxdur
        return redirect(url_for('xss_reflected', username=username))
    else:
        username = request.args.get('username', '')
    return render_template('reflected.html', username=username)

@app.route('/xss/stored', methods=['GET', 'POST'])
def xss_stored():
    db = get_db()
    if request.method == 'POST':
        username = request.form.get('username', 'Anonymous')
        book_title = request.form.get('book_title', '')
        review = request.form.get('review', '')
        db.execute("INSERT INTO reviews (username, book_title, review) VALUES (?, ?, ?)",
                   (username, book_title, review))
        db.commit()
        return redirect(url_for('xss_stored'))
    reviews = db.execute("SELECT username, book_title, review FROM reviews ORDER BY id DESC").fetchall()
    return render_template('stored.html', reviews=reviews)

@app.route('/xss/dom')
def xss_dom():
    return render_template('dom.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
