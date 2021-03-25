from flask import Flask, render_template, request, session, redirect
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

@app.route('/signup', methods=['GET', 'POST'])
def render_signup():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password2 != password:
            return redirect('/signup?error=Passwords+do+not+match.')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+at+least+8+characters+long.')

        # Create the connection
        con = create_connection(DB_NAME)

        # Run the query
        query = "INSERT INTO customers (id, fname, lname, email, password) VALUES (null, ?, ?, ?, ?)"

        cur = con.cursor()
        cur.execute(query, (fname, lname, email, password))
        con.commit()
        con.close()

    return render_template('signup.html')

if __name__ == '__main__':
    app.run()
