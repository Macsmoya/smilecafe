from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error

from flask_bcrypt import Bcrypt

DB_NAME = "smile.db"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ashjsrf77755kl%^$##"


def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None


@app.route('/', methods=["GET", "POST"])
def render_homepage():
    if request.method == "POST" and is_logged_in():
        catName = request.form['catName'].strip().title()
        if len(catName) < 3:
            return redirect("/?error=Name+must+be+at+least+3+letters+long.")
        else:
            # connect to the database
            con = create_connection(DB_NAME)

            query = "INSERT INTO categories (id, cat_name) VALUES(NULL, ?)"

            cur = con.cursor()  # You need this line next
            try:
                cur.execute(query, (catName, ))  # this line actually executes the query
            except:
                return redirect('/menu?error=Unknown+error')

            con.commit()
            con.close()

    return render_template('home.html', logged_in=is_logged_in())


@app.route('/menu/<catID>', methods=["GET", "POST"])
def render_menu_page(catID):
    if request.method == "POST" and is_logged_in():
        name = request.form['name'].strip().title()
        description = request.form['description'].strip()
        volume = request.form['volume'].strip()
        price = request.form['price']

        if len(name) < 3:
            return redirect("/menu?error=Name+must+be+at+least+3+letters+long.")
        elif len(description) < 10:
            return redirect("/menu?error=Description+must+be+at+least+10+letters+long.")
        elif len(volume) < 3:
            return redirect("/menu?error=Volume+must+be+at+least+3+letters+long.")
        else:
            # connect to the database
            con = create_connection(DB_NAME)

            query = "INSERT INTO products (id, name, description, volume, image, price, catID) " \
                "VALUES(NULL, ?, ?, ?, 'noimage', ?,?)"

            cur = con.cursor()  # You need this line next
            try:
                cur.execute(query, (name, description, volume, price, catID))  # this line actually executes the query
            except:
                return redirect('/menu?error=Unknown+error')

            con.commit()
            con.close()

    # connect to the database
    con = create_connection(DB_NAME)
    query = "SELECT id, cat_name FROM categories"
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    category_list = cur.fetchall()  # puts the results into a list usable in python

    # SELECT the things you want from your table(s)
    query = "SELECT name, description, volume, image, price, id " \
            "FROM products WHERE catID=?"

    cur = con.cursor()  # You need this line next
    cur.execute(query, (catID, ))  # this line actually executes the query
    product_list = cur.fetchall()  # puts the results into a list usable in python
    con.close()

    return render_template('menu.html', products=product_list, categories=category_list, logged_in=is_logged_in())


@app.route('/contact')
def render_contact_page():
    return render_template('contact.html', logged_in=is_logged_in())


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in():
        return redirect('/')
    print(request.form)
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM customers WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # if given the email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty resultset
        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        session['cart'] = []
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)

        query = "INSERT INTO customers (id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


app.run(host='0.0.0.0', debug=True)
