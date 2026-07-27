# Import Flask modules for web functionality
from flask import Flask, render_template, request, redirect
import sqlite3

# Create Flask application instance
app = Flask(__name__)

# Set the database filename
DATABASE = "festify.db"

# Function to create the database table if it doesn't exist
def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # SQL command to create a table for decor items
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
    
    # Save changes and close connection
    connection.commit()
    connection.close()

# Route for the homepage
@app.route("/")
def index():
    # Display the index.html template
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_decor():
    # get form data
    decor_name = request.form.get("decor_name")
    event_type = request.form.get("event_type")
    color_scheme = request.form.get("color_scheme")
    description = request.form.get("description")
    price = request.form.get("price")
    
    # check if all fields are filled
    if not decor_name:
        return render_template("index.html", error="Decor Name is required")
    if not event_type:
        return render_template("index.html", error="Event Type is required")
    if not color_scheme:
        return render_template("index.html", error="Color Scheme is required")
    if not description:
        return render_template("index.html", error="Description is required")
    if not price:
        return render_template("index.html", error="Price is required")
    
    # check if decor_name contains only letters and spaces
    if not all(char.isalpha() or char.isspace() for char in decor_name):
        return render_template("index.html", error="Decor Name must contain only letters and spaces")
    
    # check if event_type contains only letters and spaces
    if not all(char.isalpha() or char.isspace() for char in event_type):
        return render_template("index.html", error="Event Type must contain only letters and spaces")
    
    # check if color_scheme contains only letters, spaces, and & symbol
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ &")
    if not all(char in allowed_chars for char in color_scheme):
        return render_template("index.html", error="Color Scheme must contain only letters, spaces, and &")
    
    # check if description contains only letters, spaces, and basic punctuation
    allowed_desc = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,!?-")
    if not all(char in allowed_desc for char in description):
        return render_template("index.html", error="Description must contain only letters, spaces, and basic punctuation")
    
    # check if price is a valid number
    try:
        price_float = float(price)
    except ValueError:
        return render_template("index.html", error="Price must be a valid number")
    
    # check if price is greater than 0
    if price_float <= 0:
        return render_template("index.html", error="Price must be greater than $0")
    
    # connect to database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # insert the new decor item
    cursor.execute("""
        INSERT INTO decor (decor_name, event_type, color_scheme, description, price)
        VALUES (?, ?, ?, ?, ?)
    """, (decor_name, event_type, color_scheme, description, price_float))
    
    connection.commit()
    connection.close()

    # redirect to decor page
    return redirect("/decor")
    
# Route to display all decor items
@app.route("/decor")
def view_decor():
    # Connect to the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM decor")
    decor_items = cursor.fetchall()
    # Get all records from the decor table
    connection.close()
    # Display the decor.html template with the data
    return render_template("decor.html", decor_items=decor_items)

# Run the app when this file is executed directly
if __name__ == "__main__":
    create_database()
    app.run(debug=True)