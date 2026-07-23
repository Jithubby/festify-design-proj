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

# Route to handle form submission (POST request)
@app.route("/add", methods=["POST"])
 # Get form data from the user's submission
def add_decor():
    decor_name = request.form["decor_name"]
    event_type = request.form["event_type"]
    color_scheme = request.form["color_scheme"]
    description = request.form["description"]
    price = request.form["price"]
    
    # Connect to the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # Insert the new decor item into the database
    cursor.execute("""
        INSERT INTO decor (decor_name, event_type, color_scheme, description, price)
        VALUES (?, ?, ?, ?, ?)
    """, (decor_name, event_type, color_scheme, description, price))
    
    # Save changes and close connection
    connection.commit()
    connection.close()

    # Redirect user to the decor page to see all items
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