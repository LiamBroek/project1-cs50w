import os


import json
import requests
import datetime
from flask import Flask, session, render_template, request, url_for, jsonify, redirect
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.static_folder = 'static'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Variables
key = 'AwI4eR39qXj3XXLLbbKmjA'


@app.route("/")
def index():
    return render_template("index.html")





@app.route("/login", methods=["GET", "POST"])
def login():

	registerValid = True
	if request.method == 'POST':
		# register a user
		# get data
		fname = request.form.get('fname')
		sname = request.form.get('sname')
		username =  request.form.get('username')
		password = request.form.get('password')
		repassword = request.form.get('repassword')
		email = request.form.get('email')

		# ensure all fields are filled in and that password is more than 6 character
		if fname is None or sname is None or username is None or len(password) <= 6 or password!=repassword:
			registerValid = False
			return render_template('register.html', registerValid=registerValid)
		
		# registerValid = True
		# see if username doesn't already exist, if not, register user

		if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
			db.execute("INSERT INTO users (fname, sname, username, password, email) VALUES (:fname, :sname, :username, :password, :email)",
				{"fname": fname, "sname": sname, "username": username, "password": password, "email": email})
			db.commit()
	
	return render_template("login.html")
	





@app.route("/register")
def register():
	return render_template("register.html")







@app.route("/search", methods=["GET", "POST"])
def search():
	if request.method == "POST":
		# get data
		username = request.form.get('username')
		password = request.form.get('password')
		bValid = True;

		# check if data is valid
		if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount ==1:
			session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
			return render_template("search.html", username=username)
		bValid = False
		return render_template("login.html", bValid=bValid)


	if request.method == "GET":
		user = session.get('user_id')
		if user != None:
			username = db.execute("SELECT username FROM users WHERE id = :id", {"id" : session['user_id'][0]}).fetchone()
			return render_template("search.html", username=username[0])
		return jsonify({"Error": "You are not logged in"}), 404

	



@app.route("/results", methods=["POST"])
def results():
	search_request = request.form.get('search')
	search = "%" + search_request + "%"

	username = db.execute("SELECT username FROM users WHERE id = :id", {"id" : session['user_id'][0]}).fetchone()

	results = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR title LIKE :search OR author LIKE :search", {"search" : search}).fetchall()

	return render_template("results.html", results=results, search=search_request, username=username)








@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):

	book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"book_id" : book_id}).fetchone()
	
	isbn = book.isbn


	res = requests.get("https://www.goodreads.com/book/review_counts.json?", params={"key":key, "isbns":isbn})
	if res.status_code != 200:
		raise ValueError
	data = res.json()
	numRatings = data["books"][0]["ratings_count"]
	aveRating = data["books"][0]["average_rating"]

	username = db.execute("SELECT username FROM users WHERE id = :id", {"id" : session['user_id'][0]}).fetchone()
	bReview = True
	reviews = db.execute("SELECT username, user_id, review FROM reviews JOIN users ON users.id = user_id WHERE book_id = :book_id", {"book_id" : book_id }).fetchall()
	for review in reviews:
		if review.user_id == session['user_id'][0]:
			bReview = False

	if request.method == 'POST':
		if bReview == True:
			rating = request.form.get('rating')
			review = request.form.get('review')
			db.execute("INSERT INTO reviews (user_id, book_id, review, rating) VALUES (:user_id, :book_id, :review, :rating)", {'user_id' : session['user_id'][0], 'book_id':book.book_id, 'review':review, 'rating':rating})
			db.commit()
			bReview = False
			reviews = db.execute("SELECT username, user_id, review FROM reviews JOIN users ON users.id = user_id WHERE book_id = :book_id", {"book_id" : book_id }).fetchall()
			return render_template("book.html", book=book, reviews=reviews, bReview=bReview, username=username, numRatings=numRatings, aveRating=aveRating)
		return render_template("book.html", book=book, reviews=reviews, bReview=bReview, username=username, numRatings=numRatings, aveRating=aveRating)
	return render_template("book.html", book=book, reviews=reviews, bReview=bReview, username=username, numRatings=numRatings, aveRating=aveRating)

	



@app.route("/api/<string:isbn>")
def book_api(isbn):

	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
	if book is None:
		return jsonify({"error": "Invalid ISBN"}), 404

	res = requests.get("https://www.goodreads.com/book/review_counts.json?", params={"key":key, "isbns":isbn})
	if res.status_code != 200:
		raise ValueError
	data = res.json()
	numReviews = data["books"][0]["reviews_count"]
	aveRating = data["books"][0]["average_rating"]

	
	return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": book.isbn,
    "review_count": numReviews,
    "average_score": aveRating
	})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))














