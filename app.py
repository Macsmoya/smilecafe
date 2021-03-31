from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error

DB_NAME = "smile.db"

app = Flask(__name__)
app.secret_key = "kzdjflawyrtp9v8awto;micstawnt;ihtg"

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
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = "SELECT id, fname, password FROM customers WHERE email = ?"
        # Create the connection
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email))
        user_data = cur.fetchall()
        con.close()

        # If the email address is in the database, the user_data
        # will hold the information we need.

        try:
            userid = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+address+or+password+incorrect")

        # Check if the password is correct or not
        if password != db_password:
            return redirect("/login?error=Email+address+or+password+incorrect")

        # Set up a session and store some useful data
        session['email'] = email
        session['userid'] = userid
        session['first_name'] = first_name
        print(session)
        return redirect('/')
    return render_template('login.html', logged_in = is_logged_in())



    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def render_signup():
    if request.method == 'POST':
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
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
        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+address+already+in+use.')
        con.commit()
        con.close()
        return redirect("/login")

    return render_template('signup.html')

if __name__ == '__main__':
    app.run()
