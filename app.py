from flask import Flask, render_template, request, redirect, session
import sqlite3 
import requests
from flask_mail import Mail, Message
from datetime import datetime
import openai

app = Flask(__name__)
app.secret_key = 'festify_secret_key'
# Gmail SMTP configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'festifyau@gmail.com'
app.config['MAIL_PASSWORD'] = 'gxuk dpmq hkge iogm'  # App password
app.config['MAIL_DEFAULT_SENDER'] = 'festifyau@gmail.com'

mail = Mail(app)


DATABASE = "festify.db"

# admin credentials (from SRS)
ADMIN_USERNAME = "anita"
ADMIN_PASSWORD = "decor2024"

# unsplash api key (get from unsplash.com)
UNSPLASH_ACCESS_KEY = "44Fxyn--Fv1yJNwNAiCVPoEFRt7fZNv80ikmCdEZZIc"

# Agnes AI configuration (after your other configs)
AGNES_API_KEY = "sk-Xb4JdXX1ueAcR0csBYLZTWyYeZev25SbKnma6Qm3q9SwqLxF"  
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

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

# email confirmation
def send_order_confirmation(customer_email, customer_name, order_details):
    """Sends an order confirmation email to the customer."""
    try:
        print(f"📧 Attempting to send email to: {customer_email}")
        
        msg = Message(
            subject="Your Festify Order is Confirmed!",
            recipients=[customer_email],
            sender='friedricebombed@gmail.com'
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #6C63FF; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">🎨 Festify</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #6C63FF;">Thank you for your order, {customer_name}!</h2>
                <p>Your order has been received and we'll be in touch soon.</p>
                
                <h3 style="color: #6C63FF; margin-top: 30px;">Order Summary</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Event Type:</strong></td>
                        <td style="padding: 8px 0;">{order_details['event_type']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Decor Style:</strong></td>
                        <td style="padding: 8px 0;">{order_details['decor_style']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Color Scheme:</strong></td>
                        <td style="padding: 8px 0;">{order_details.get('color_scheme', 'Not specified')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Event Date:</strong></td>
                        <td style="padding: 8px 0;">{order_details['event_date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Venue:</strong></td>
                        <td style="padding: 8px 0;">{order_details.get('venue', 'Not specified')}</td>
                    </tr>
                </table>
                
                <div style="background: #f0f0ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 0; color: #555;"><strong>Special Requests:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #666;">{order_details.get('special_requests', 'None')}</p>
                </div>
                
                <p style="margin-top: 30px; color: #888; font-size: 0.9rem;">— The Festify Team</p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✅ Confirmation email sent to {customer_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def get_ai_response(user_message):
    """Gets a response from Agnes AI for the chatbot."""
    try:
        client = openai.OpenAI(
            api_key=AGNES_API_KEY,
            base_url=AGNES_BASE_URL
        )
        
        response = client.chat.completions.create(
            model="agnes-2.0-flash",
            messages=[
                {"role": "system", "content": """You are a strict event decor assistant for Festify. 
You ONLY answer questions about:
- Decor ideas and inspiration
- Color schemes and themes
- Event planning for weddings, birthdays, baby showers, engagements, graduations, and corporate events
- Decor styles and trends
- Festify's services and ordering process

If a question is NOT about decor, events, or Festify, politely respond:
"I'm sorry, I can only answer questions about event decor and Festify. How can I help with your event planning?"

Do NOT answer any questions outside these topics. Be friendly and helpful for decor-related questions."""},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "Sorry, I'm having trouble connecting right now. Please try again later."

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
    
    # get past orders for inspiration (only last 6)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 6")
    past_orders = cursor.fetchall()
    connection.close()
    
    # get unsplash images based on past orders
    unsplash_images = []
    if past_orders:
        event_type = past_orders[0][4] if len(past_orders[0]) > 4 else "event"
        search_term = f"{event_type} decoration ideas"
        unsplash_images = get_unsplash_images(search_term, 6)
    else:
        unsplash_images = get_unsplash_images("event decoration ideas", 6)
    
    return render_template("decor.html", 
                         decor_items=decor_items, 
                         unsplash_images=unsplash_images,
                         past_orders=past_orders)
    
    
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
        # send confirmation email
    order_details = {
        'event_type': event_type,
        'decor_style': decor_style,
        'color_scheme': color_scheme,
        'event_date': event_date,
        'venue': venue,
        'special_requests': special_requests
    }
    send_order_confirmation(email, customer_name, order_details)
    
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

@app.route("/admin/stats")
def admin_stats():
    if not session.get('logged_in'):
        return redirect("/login")
    
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # count by status
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'In Progress'")
    progress_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'")
    completed_count = cursor.fetchone()[0]
    
    # orders by event type
    cursor.execute("""
        SELECT event_type, COUNT(*) FROM orders 
        GROUP BY event_type 
        ORDER BY COUNT(*) DESC
    """)
    event_counts = cursor.fetchall()
    
    # most popular decor styles
    cursor.execute("""
        SELECT decor_style, COUNT(*) FROM orders 
        GROUP BY decor_style 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    """)
    popular_decor = cursor.fetchall()
    
    connection.close()
    
    return render_template("admin_stats.html", 
                         total_orders=total_orders,
                         pending_count=pending_count,
                         progress_count=progress_count,
                         completed_count=completed_count,
                         event_counts=event_counts,
                         popular_decor=popular_decor)

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot messages."""
    user_message = request.form.get("message")
    
    if not user_message:
        return {"error": "No message provided"}, 400
    
    ai_reply = get_ai_response(user_message)
    return {"reply": ai_reply}

if __name__ == "__main__":
    create_database()
    app.run(debug=True)


