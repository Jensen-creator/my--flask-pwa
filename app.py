from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session

# Initialize the database
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    # Table for items
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home page: show items for sale
@app.route('/')
def index():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    cart = session.get('cart', [])
    return render_template('index.html', items=items, cart=cart)

# Add a new item to sell
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        if name and price:
            conn = sqlite3.connect('shop.db')
            c = conn.cursor()
            c.execute('INSERT INTO items (name, price) VALUES (?, ?)', (name, float(price)))
            conn.commit()
            conn.close()
            return redirect('/')
    return render_template('add_item.html')

# Add item to cart
@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    cart = session.get('cart', [])
    cart.append(item_id)
    session['cart'] = cart
    return redirect('/')

# View cart
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    items_in_cart = []
    total = 0
    for item_id in cart:
        c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = c.fetchone()
        if item:
            items_in_cart.append(item)
            total += item[2]  # price
    conn.close()
    return render_template('cart.html', items=items_in_cart, total=total)

if __name__ == '__main__':
    app.run(debug=True)
