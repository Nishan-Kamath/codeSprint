from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    connection = sqlite3.connect('LoginData.db')
    cursor = connection.cursor()

    user = cursor.execute("SELECT * FROM USERS WHERE email=? AND password=?",(email,password)).fetchall()
    connection.close()
    if len(user) > 0:
        return redirect(f'/home?fname={user[0][0]}&lname={user[0][1]}&email={user[0][2]}')
    else:
        return redirect('/')
    
@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/home')
def home():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    email = request.args.get('email')

    return render_template('home.html',fname=fname, lname=lname, email=email)

@app.route('/add_user',methods=['POST'])
def add_user():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')

    connection = sqlite3.connect('LoginData.db')
    cursor = connection.cursor()

    ans = cursor.execute("select * from USERS where email=? AND password=?",(email,password)).fetchall()

    if len(ans) > 0:
        connection.close()
        return render_template('login.html')
    else:
        cursor.execute("INSERT INTO USERS(first_name,last_name,email,password)values(?,?,?,?)",(fname,lname,email,password))
        connection.commit()
        connection.close()
        return render_template('login.html')
    
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    connection = sqlite3.connect('LoginData.db')
    cursor = connection.cursor()
    
    # Initialize items to avoid UnboundLocalError
    items = []
    
    if request.method == 'POST':
        # Get form data to add a new item
        foodname = request.form['food-name']
        quantity = request.form['quantity']
        expiry_date = request.form['expiry-date']
        door_no = request.form['door-no']
        
        # Insert data into the database
        cursor.execute(
            "INSERT INTO INVENTORY (foodname, quantity, expiry, door_no) VALUES (?, ?, ?, ?)",
            (foodname, quantity, expiry_date, door_no)
        )
        connection.commit()
        flash("New item added successfully!")  # Add flash message
        return redirect(url_for('inventory'))
    
    if request.method == 'GET' and 'door-no' in request.args:
        # Get the door number from query parameters
        door_no = request.args['door-no']
        
        # Fetch items for the given door number
        items = cursor.execute(
            "SELECT * FROM INVENTORY WHERE door_no = ?", (door_no,)
        ).fetchall()
    else:
        # Fetch all items if no door number is specified
        items = cursor.execute("SELECT * FROM INVENTORY").fetchall()
    
    connection.close()
    return render_template('inventory.html', items=items)


@app.route('/delete/<string:foodname>', methods=['POST'])
def delete_item(foodname):
    connection = sqlite3.connect('LoginData.db')
    cursor = connection.cursor()
    
    try:
        # Delete the item from the database using the item_id
        cursor.execute("DELETE FROM INVENTORY WHERE foodname = ?", (foodname,))
        connection.commit()
    except Exception as e:
        print(f"Error deleting item: {e}")
    finally:
        connection.close()
    
    # Redirect back to the inventory page
    return redirect('/inventory')



if __name__ == '__main__':
    app.run(debug=True)