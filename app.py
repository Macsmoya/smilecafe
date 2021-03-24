from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

DB_NAME = "smile.db"

app = Flask(__name__)

def create_connection(db_file):
    # Creates a connection to the database
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

@app.route('/')
def render_home():
    return render_template('home.html')

@app.route('/contact')
def render_contact():
    return render_template('contact.html')

@app.route('/menu')
def render_menu():

    # Create the connection
    con = create_connection(DB_NAME)

    # Run the query
    query = "SELECT name, description, volume, image, price FROM products"

    cur = con.cursor()
    cur.execute(query)
    product_list = cur.fetchall()
    con.close()

    return render_template('menu.html', products=product_list)

@app.route('/login')
def render_login():
    return render_template('login.html')

@app.route('/signup')
def render_signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run()
