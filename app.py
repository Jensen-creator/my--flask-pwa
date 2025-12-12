from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize database
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
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

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handle adding a new item
    if request.method == 'POST' and request.form.get('action') == 'add_item':
        name = request.form.get('name')
        price = request.form.get('price')
        if name and price:
            conn = sqlite3.connect('shop.db')
            c = conn.cursor()
            c.execute('INSERT INTO items (name, price) VALUES (?, ?)', (name, float(price)))
            conn.commit()
            conn.close()
        return redirect('/')

    # Handle adding to cart
    item_id = request.args.get('add_to_cart')
    if item_id:
        cart = session.get('cart', [])
        cart.append(int(item_id))
        session['cart'] = cart
        return redirect('/')

    # Fetch items and cart info (single connection)
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()

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
