from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
db_file = 'LoginData.db'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    user = cursor.execute("SELECT * FROM USERS WHERE email=? AND password=?", (email, password)).fetchall()
    connection.close()
    if len(user) > 0:
        return redirect(f'/home?fname={user[0][0]}&lname={user[0][1]}&email={user[0][2]}')
    else:
        flash("Invalid email or password")
        return redirect('/')

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/home')
def home():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    email = request.args.get('email')

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Fetch donation history for the logged-in user
    donations = cursor.execute(
        "SELECT foodname, quantity, donation_date, service FROM DONATION WHERE email=?", (email,)
    ).fetchall()

    # Query to fetch top 10 donors based on total donations
    leaderboard = cursor.execute("""
        SELECT first_name, last_name, SUM(quantity) AS total_donations
        FROM DONATION
        GROUP BY first_name, last_name
        ORDER BY total_donations DESC
        LIMIT 10
    """).fetchall()

    connection.close()
    return render_template('home.html', fname=fname, lname=lname, email=email, donations=donations, leaderboard=leaderboard)

@app.route('/add_user', methods=['POST'])
def add_user():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    door_no = request.form.get('door_no')

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    user_exists = cursor.execute("SELECT * FROM USERS WHERE email=?", (email,)).fetchall()

    if len(user_exists) > 0:
        connection.close()
        flash("User already exists. Please log in.")
        return render_template('login.html')
    else:
        cursor.execute("INSERT INTO USERS(first_name, last_name, email, password,door_no) VALUES (?, ?, ?, ?,?)", 
                       (fname, lname, email, password,door_no))
        connection.commit()
        connection.close()
        flash("Sign-up successful! Please log in.")
        return render_template('login.html')

@app.route('/add_donation', methods=['POST'])
def add_donation():
    fname = request.form.get('first_name')
    lname = request.form.get('last_name')
    email = request.form.get('email')
    foodname = request.form.get('foodname')
    quantity = request.form.get('quantity')
    donation_date = request.form.get('donation_date')
    service = request.form.get('service')

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO DONATION(first_name, last_name, email, foodname, quantity, donation_date, service) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fname, lname, email, foodname, quantity, donation_date, service)
        )
        connection.commit()
        flash("Donation added successfully!")
    except Exception as e:
        flash(f"Error adding donation: {e}")
    finally:
        connection.close()

    return redirect(f'/home?fname={fname}&lname={lname}&email={email}')

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    items = []

    if request.method == 'POST':
        foodname = request.form['food-name']
        quantity = request.form['quantity']
        expiry_date = request.form['expiry-date']
        door_no = request.form['door-no']

        cursor.execute(
            "INSERT INTO INVENTORY (foodname, quantity, expiry, door_no) VALUES (?, ?, ?, ?)",
            (foodname, quantity, expiry_date, door_no)
        )
        connection.commit()
        flash("New item added successfully!")
        return redirect(url_for('inventory'))

    if request.method == 'GET' and 'door-no' in request.args:
        door_no = request.args['door-no']
        items = cursor.execute(
            "SELECT * FROM INVENTORY WHERE door_no = ?", (door_no,)
        ).fetchall()
    else:
        items = cursor.execute("SELECT * FROM INVENTORY").fetchall()

    connection.close()
    return render_template('inventory.html', items=items)

@app.route('/delete/<string:foodname>', methods=['POST'])
def delete_item(foodname):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM INVENTORY WHERE foodname = ?", (foodname,))
        connection.commit()
    except Exception as e:
        print(f"Error deleting item: {e}")
    finally:
        connection.close()

    return redirect('/inventory')

if __name__ == '__main__':
    # Ensure tables exist
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS(
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DONATION(
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            foodname TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            donation_date DATE NOT NULL,
            service TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS INVENTORY(
            foodname TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry DATE NOT NULL,
            door_no TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

    app.run(debug=True)
