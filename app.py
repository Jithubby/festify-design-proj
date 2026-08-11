from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'festify_secret_key'

DATABASE = "festify.db"

# admin credentials (from SRS)
ADMIN_USERNAME = "anita"
ADMIN_PASSWORD = "decor2024"

# unsplash api key (get from unsplash.com)
UNSPLASH_ACCESS_KEY = "44Fxyn--Fv1yJNwNAiCVPoEFRt7fZNv80ikmCdEZZIc"

def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # table for decor ideas (admin adds these)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decor_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            color_scheme TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    
    # table for customer orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            event_type TEXT NOT NULL,
            decor_style TEXT NOT NULL,
            color_scheme TEXT,
            event_date TEXT NOT NULL,
            venue TEXT,
            special_requests TEXT,
            order_date TEXT NOT NULL
        )
    """)
    
    connection.commit()
    connection.close()

# unsplash api function
def get_unsplash_images(query="event decor", count=6):
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        params = {"query": query, "per_page": count, "orientation": "landscape"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        return []
    except:
        return []

# ===== ROUTES =====

# homepage
@app.route("/")
def index():
    return render_template("index.html")

# decor gallery page
@app.route("/decor")
def view_decor():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM decor")
    decor_items = cursor.fetchall()
    connection.close()
    
    images = get_unsplash_images("event decoration ideas", 6)
    
    return render_template("decor.html", decor_items=decor_items, unsplash_images=images)

# order form page
@app.route("/order")
def order_form():
    from datetime import date
    today = date.today().isoformat()
    return render_template("order.html", today=today)

# submit order
@app.route("/submit_order", methods=["POST"])
def submit_order():
    customer_name = request.form.get("customer_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    event_type = request.form.get("event_type")
    decor_style = request.form.get("decor_style")
    color_scheme = request.form.get("color_scheme")
    event_date = request.form.get("event_date")
    venue = request.form.get("venue")
    special_requests = request.form.get("special_requests")
    
    # validations
    if not customer_name:
        return render_template("order.html", error="Name is required")
    if not email:
        return render_template("order.html", error="Email is required")
    if not event_type:
        return render_template("order.html", error="Event type is required")
    if not decor_style:
        return render_template("order.html", error="Decor style is required")
    if not event_date:
        return render_template("order.html", error="Event date is required")
    
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO orders (customer_name, email, phone, event_type, decor_style, 
                           color_scheme, event_date, venue, special_requests, order_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_name, email, phone, event_type, decor_style, 
          color_scheme, event_date, venue, special_requests, order_date))
    connection.commit()
    connection.close()
    
    return render_template("confirmation.html", 
                         order={
                             'customer_name': customer_name,
                             'email': email,
                             'phone': phone,
                             'event_type': event_type,
                             'decor_style': decor_style,
                             'color_scheme': color_scheme,
                             'event_date': event_date,
                             'venue': venue,
                             'special_requests': special_requests
                         })

# admin login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

# admin dashboard
@app.route("/admin")
def admin():
    if not session.get('logged_in'):
        return redirect("/login")
    
    search_query = request.args.get('search', '')
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    if search_query:
        cursor.execute("SELECT * FROM orders WHERE customer_name LIKE ? ORDER BY id DESC", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    
    orders = cursor.fetchall()
    connection.close()
    
    return render_template("admin.html", orders=orders, search_query=search_query)

# logout
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect("/login")

# update order status
@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    if not session.get('logged_in'):
        return redirect("/login")
    
    status = request.form.get("status")
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    connection.commit()
    connection.close()
    
    return redirect("/admin")

# delete order
@app.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    if not session.get('logged_in'):
        return redirect("/login")
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    connection.commit()
    connection.close()
    
    return redirect("/admin")

if __name__ == "__main__":
    create_database()
    app.run(debug=True)