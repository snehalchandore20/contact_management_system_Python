from flask import Flask, render_template, request, redirect, flash
from db import get_connection
import re

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------------
# Email Validation Function 
# -------------------------------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# -------------------------------
# Phone Validation Function 
# -------------------------------
def is_valid_phone(phone):
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone)

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

    # Email validation
    if not is_valid_email(email):
        flash("Invalid Email Format!", "danger")
        return redirect('/')

    # Phone validation
    if not is_valid_phone(phone):
        flash("Phone must be exactly 10 digits!", "danger")
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate FULL record check 
    cursor.execute("""
        SELECT * FROM contacts 
        WHERE first=%s AND last=%s AND phone=%s AND email=%s
    """, (first, last, phone, email))

    if cursor.fetchone():
        conn.close()
        flash("Duplicate contact not allowed!", "danger")
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
# DELETE CONTACT
# -------------------------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    flash("Contact deleted successfully!", "success")
    return redirect('/')

# -------------------------------
# EDIT PAGE
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
        flash("Required fields missing!", "danger")
        return redirect('/')

    # Email validation
    if not is_valid_email(email):
        flash("Invalid Email Format!", "danger")
        return redirect('/')

    # Phone validation
    if not is_valid_phone(phone):
        flash("Phone must be exactly 10 digits!", "danger")
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate check 
    cursor.execute(
        "SELECT * FROM contacts WHERE email=%s AND id!=%s",
        (email, id)
    )

    if cursor.fetchone():
        conn.close()
        flash("Email already used by another contact!", "danger")
        return redirect('/')

    # Update data
    cursor.execute(
        "UPDATE contacts SET first=%s, last=%s, address=%s, email=%s, phone=%s WHERE id=%s",
        (first, last, address, email, phone, id)
    )
    conn.commit()
    conn.close()

    flash("Contact updated successfully!", "success")
    return redirect('/')

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)