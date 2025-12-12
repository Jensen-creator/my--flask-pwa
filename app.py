from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()

    # Handle new item submission
    if request.method == 'POST' and request.form.get('action') == 'add_item':
        name = request.form.get('name')
        price = request.form.get('price')
        image_file = request.files.get('image')
        image_filename = None

        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        if name and price:
            try:
                price = float(price)
            except ValueError:
                return "Invalid price!", 400
            c.execute('INSERT INTO items (name, price, image) VALUES (?, ?, ?)',
                      (name, price, image_filename))
            conn.commit()
        return redirect('/')

    # Handle adding to cart
    item_id = request.args.get('add_to_cart')
    if item_id:
        cart = session.get('cart', [])
        cart.append(int(item_id))
        session['cart'] = cart
        return redirect('/')

    # Handle search
    search_query = request.args.get('search')
    if search_query:
        c.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + search_query + '%',))
    else:
        c.execute("SELECT * FROM items")
    items = c.fetchall()

    # Fetch cart items
    cart = session.get('cart', [])
    cart_items = []
    total = 0
    for i in cart:
        c.execute('SELECT * FROM items WHERE id=?', (i,))
        item = c.fetchone()
        if item:
            cart_items.append(item)
            total += item[2]

    conn.close()
    return render_template('index.html', items=items, cart_items=cart_items, total=total)

if __name__ == '__main__':
    app.run(debug=True)

