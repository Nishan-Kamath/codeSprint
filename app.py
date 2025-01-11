from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import os
import smtplib
from email.message import EmailMessage

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
        cursor.execute("INSERT INTO USERS(first_name, last_name, email, password, door_no) VALUES (?, ?, ?, ?, ?)", 
                       (fname, lname, email, password, door_no))
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

@app.route('/waste', methods=['GET', 'POST'])
def waste():
    if request.method == 'POST':
        # Fetch user inputs
        food_item = request.form.get('food_item')
        is_cooked = request.form.get('cooked')
        is_packed = request.form.get('plastic_packed')
        amount = request.form.get('food_amount')

        # Waste categorization logic
        if food_item in ['vegetables', 'fruits'] and is_cooked == 'no' and is_packed == 'off':
            result = f"{amount} of {food_item} can be composted."
        elif food_item == 'meat' or is_cooked == 'yes':
            result = f"{amount} of {food_item} should be disposed of carefully. Do not compost cooked or meat items."
        elif is_packed == 'on':
            result = f"Remove plastic packaging from {food_item} before disposal."
        else:
            result = f"{amount} of {food_item} does not fit composting requirements. Dispose of appropriately."

        return render_template('waste.html', result=result)

    # Initial GET request
    return render_template('waste.html', result=None)

@app.route('/donation')
def donation():
    return render_template('donate.html')

@app.route('/chat-bot')
def chat_bot():
    return render_template('chat-bot.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/achievements')
def achievements():
    return render_template('achievements.html')

# Fundraising and Donation route
@app.route('/fundraising', methods=['GET', 'POST'])
def fundraising():
    donation_amount = None
    if request.method == 'POST':
        donation_amount = request.form['donation-amount']
        # Process the donation here (e.g., saving to a database, etc.)
        print(f"Donation received: ${donation_amount}")  # Debugging print
    return render_template('fundraising_donation.html', donation_amount=donation_amount)

@app.route('/stackFood')
def stack_food():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Fetch all available food items from the DONATION table
    items = cursor.execute("SELECT foodname, quantity, email FROM DONATION").fetchall()
    connection.close()

    return render_template('stackFood.html', items=items)

@app.route('/order_food', methods=['POST'])
def order_food():
    foodname = request.form.get('foodname')

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    try:
        # Fetch the donor's email for the selected food item
        donor_data = cursor.execute("SELECT email FROM DONATION WHERE foodname = ?", (foodname,)).fetchone()
        if not donor_data:
            flash(f"No matching food item found for {foodname}.")
            return redirect('/stackFood')

        donor_email = donor_data[0]

        # Remove the ordered food item from the DONATION table
        cursor.execute("DELETE FROM DONATION WHERE foodname = ?", (foodname,))
        connection.commit()

        # Send email notifications
        recipient_email = donor_email  # Replace with the recipient's actual email
        send_email_notifications(foodname, donor_email, recipient_email)

        flash(f"{foodname} has been successfully ordered! Emails sent to donor and recipient.")
    except Exception as e:
        flash(f"Error ordering food: {e}")
    finally:
        connection.close()

    return redirect('/stackFood')


def send_email_notifications(foodname, donor_email, recipient_email):
    """Send email notifications to the donor and recipient."""
    sender_email = "nishankamath@gmail.com"  # Replace with your email
    sender_password = "@K1a2m3a4t5h6"       # Replace with your email password

    subject = f"Food Order Update: {foodname}"

    donor_message = f"""
    Hello,

    Your donated food item '{foodname}' has been successfully ordered by a recipient.
    Thank you for your generous donation!

    Regards,
    Food Donation Team
    """

    recipient_message = f"""
    Hello,

    You have successfully ordered the food item '{foodname}'.
    Please coordinate with the donor for further details.

    Regards,
    Food Donation Team
    """

    try:
        # Set up the email server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email to the donor
        donor_msg = EmailMessage()
        donor_msg.set_content(donor_message)
        donor_msg['Subject'] = subject
        donor_msg['From'] = sender_email
        donor_msg['To'] = donor_email
        server.send_message(donor_msg)

        # Send email to the recipient
        recipient_msg = EmailMessage()
        recipient_msg.set_content(recipient_message)
        recipient_msg['Subject'] = subject
        recipient_msg['From'] = sender_email
        recipient_msg['To'] = recipient_email
        server.send_message(recipient_msg)

        server.quit()

    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == '__main__':
    app.run(debug=True)
