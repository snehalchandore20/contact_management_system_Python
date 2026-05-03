from flask import Flask, render_template, request, redirect, flash
from db import get_connection
import re

app = Flask(__name__)
app.secret_key = "secret123" 

# -------------------------------
# Email Validation Function
# -------------------------------
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# -------------------------------
# HOME (Read all contacts)
# -------------------------------
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()

    conn.close()
    return render_template('index.html', contacts=contacts)

# -------------------------------
# ADD CONTACT (Create)
# -------------------------------
@app.route('/add', methods=['POST'])
def add():
    first = request.form['first']
    last = request.form['last']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']

    # Required validation
    if not first or not email or not phone:
        flash("First Name, Email and Phone are required!", "danger")
        return redirect('/')

    # Email format validation
    if not is_valid_email(email):
        flash("Invalid Email Format!", "danger")
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate email check
    cursor.execute("SELECT * FROM contacts WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        flash("Email already exists!", "danger")
        return redirect('/')

    # Insert data
    cursor.execute(
        "INSERT INTO contacts (first, last, address, email, phone) VALUES (%s,%s,%s,%s,%s)",
        (first, last, address, email, phone)
    )
    conn.commit()
    conn.close()

    flash("Contact added successfully!", "success")
    return redirect('/')

# -------------------------------
# DELETE CONTACT
# -------------------------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# -------------------------------
# EDIT PAGE (Fetch One Contact)
# -------------------------------
@app.route('/edit/<int:id>')
def edit(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contacts WHERE id=%s", (id,))
    contact = cursor.fetchone()

    conn.close()
    return render_template('edit.html', contact=contact)

# -------------------------------
# UPDATE CONTACT
# -------------------------------
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    first = request.form['first']
    last = request.form['last']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']

    # Required validation
    if not first or not email or not phone:
        return "Required fields missing!"

    # Email format validation
    if not is_valid_email(email):
        return "Invalid Email Format!"

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate check (excluding current record)
    cursor.execute(
        "SELECT * FROM contacts WHERE email=%s AND id!=%s",
        (email, id)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Email already used by another contact!"

    # Update Data
    cursor.execute(
        "UPDATE contacts SET first=%s, last=%s, address=%s, email=%s, phone=%s WHERE id=%s",
        (first, last, address, email, phone, id)
    )
    conn.commit()
    conn.close()

    return redirect('/')

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)