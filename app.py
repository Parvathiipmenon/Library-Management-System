from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector as sql
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
conn = sql.connect(host='localhost', user='root', password='devika@2004', database='library_manangment')
cur = conn.cursor()

def display_books():
    try:
        cur.execute("SELECT * FROM books")
        books = cur.fetchall()
        return books if books else []
    except Exception as e:
        return f"Error fetching books: {e}"

def add_book(BookName, Author, Dateofissue):
    try:
        LibCode = random.randint(0, 10000)
        Status = "Yes"
        book_data = (LibCode, BookName, Author, Dateofissue, Status)
        cur.execute("INSERT INTO books (LibCode, BookName, Author, Dateofissue, Status) VALUES (%s, %s, %s, %s, %s)", book_data)
        conn.commit()
        return "Book added successfully"
    except Exception as e:
        return f"Couldn't add the book: {e}"

def delete_book(BookName):
    try:
        name_ = BookName.upper()
        cur.execute("SELECT * FROM books WHERE UPPER(BookName) = %s", (name_,))
        book = cur.fetchone()
        if book:
            cur.execute("DELETE FROM books WHERE UPPER(BookName) = %s", (name_,))
            conn.commit()
            return "Book Deleted successfully"
        else:
            return "No such book"
    except Exception as e:
        return f"Couldn't delete the book: {e}"

def register_member(LNo, Name, age, DOJ, Address, Phno, pwd):
    try:
        member_data = (LNo, Name, age, DOJ, Address, Phno, pwd)
        cur.execute("INSERT INTO members (LNo, Name, age, DOJ, Address, Phno, Pwd) VALUES (%s, %s, %s, %s, %s, %s, %s)", member_data)
        conn.commit()
        return "Account created successfully"
    except Exception as e:
        return f"Error creating account: {e}"

def take_book(BN, member_name):
    try:
        cur.execute("SELECT * FROM books WHERE BookName = %s", (BN,))
        book = cur.fetchone()
        if book:
            if book[4].lower() == "yes":
                Datetaken = datetime.now().strftime("%Y-%m-%d")
                Dategiven = None
                Status = "No"
                data = (book[0], Datetaken, Dategiven, member_name, Status)
                cur.execute("UPDATE books SET Status = %s WHERE LibCode = %s", (Status, book[0]))
                cur.execute("INSERT INTO records (LibCode, Datetaken, Dategiven, Name, Status) VALUES (%s, %s, %s, %s, %s)", data)
                conn.commit()
                return "Book issued successfully"
            else:
                return "Sorry, this book is already taken."
        else:
            return "Sorry, this book does not exist."
    except Exception as e:
        return f"Error taking book: {e}"

def return_book(BookName):
    try:
        cur.execute("SELECT * FROM books WHERE BookName = %s", (BookName,))
        book = cur.fetchone()
        if book:
            cur.execute("UPDATE books SET Status = %s WHERE LibCode = %s", ("Yes", book[0]))
            cur.execute("DELETE FROM records WHERE LibCode = %s", (book[0],))
            conn.commit()
            return "Book returned successfully"
        else:
            return "No such book"
    except Exception as e:
        return f"Error returning book: {e}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
        p = cur.fetchall()
        if any(p):
            return redirect(url_for('admin_page'))
        else:
            flash("Access denied. Try again.")
    return render_template('admin_login.html')

@app.route('/admin_page')
def admin_page():
    books = display_books()
    return render_template('admin_page.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book_route():
    BookName = request.form['book_name']
    Author = request.form['author']
    Dateofissue = request.form['date_of_issue']
    result = add_book(BookName, Author, Dateofissue)
    flash(result)
    return redirect(url_for('admin_page'))

@app.route('/delete_book', methods=['POST'])
def delete_book_route():
    BookName = request.form['book_name']
    result = delete_book(BookName)
    flash(result)
    return redirect(url_for('admin_page'))

@app.route('/user', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        LNo = request.form['username']
        pwd = request.form['password']
        cur.execute("SELECT * FROM members WHERE LNo = %s AND Pwd = %s", (LNo, pwd))
        member = cur.fetchone()
        if member:
            return redirect(url_for('user_page', member_name=member[1]))
        else:
            flash("Invalid username or password. Please try again.")
    return render_template('user_login.html')

@app.route('/user_page/<member_name>')
def user_page(member_name):
    books = display_books()
    return render_template('user_page.html', books=books, member_name=member_name)

@app.route('/take_book', methods=['POST'])
def take_book_route():
    BN = request.form['book_name']
    member_name = request.form['member_name']
    result = take_book(BN, member_name)
    flash(result)
    return redirect(url_for('user_page', member_name=member_name))

@app.route('/return_book', methods=['POST'])
def return_book_route():
    BookName = request.form['book_name']
    member_name = request.form['member_name']
    result = return_book(BookName)
    flash(result)
    return redirect(url_for('user_page', member_name=member_name))

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        LNo = request.form['username']
        Name = request.form['name']
        age = request.form['age']
        DOJ = request.form['doj']
        Address = request.form['address']
        Phno = request.form['phno']
        pwd = request.form['password']
        result = register_member(LNo, Name, age, DOJ, Address, Phno, pwd)
        flash(result)
        return redirect(url_for('home'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
