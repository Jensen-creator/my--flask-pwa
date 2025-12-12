from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"

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

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row  # enable dictionary-style access
    return conn

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    c = conn.cursor()

    # Add new item
    if request.method == 'POST' and request.form.get('action') == 'add_item':
        name = request.form.get('name').strip()
        price = request.form.get('price').strip()
        image_file = request.files.get('image')
        image_filename = None

        if image_file and allowed_file(image_file.filename):
            image_filename = str(uuid.uuid4()) + "_" + secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        if not name or not price:
            flash("Name and price are required!")
            return redirect('/')

        try:
            price = float(price)
        except ValueError:
            flash("Invalid price!")
            return redirect('/')

        c.execute('INSERT INTO items (name, price, image) VALUES (?, ?, ?)',
                  (name, price, image_filename))
        conn.commit()
        flash(f"Item '{name}' added successfully!")
        return redirect('/')

    # Add to cart
    item_id = request.args.get('add_to_cart')
    if item_id:
        cart = session.get('cart', {})
        cart[item_id] = cart.get(item_id, 0) + 1
        session['cart'] = cart
        flash("Item added to cart!")
        return redirect('/')

    # Search items
    search_query = request.args.get('search')
    if search_query:
        c.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + search_query + '%',))
    else:
        c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()

    return render_template('index.html', items=items)

@app.route('/cart')
def cart():
    conn = get_db_connection()
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for item_id, qty in cart.items():
        item = conn.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        if item:
            subtotal = item['price'] * qty
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'image': item['image'],
                'quantity': qty,
                'subtotal': subtotal
            })
            total += subtotal
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/remove/<int:item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    item_id_str = str(item_id)
    if item_id_str in cart:
        del cart[item_id_str]
        session['cart'] = cart
        flash("Item removed from cart!")
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)
