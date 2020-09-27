import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT * FROM users WHERE id = :sessid",
                          sessid=session["user_id"])
    return apology("Welcome inside", rows[0]["username"])


@ app.route("/buy", methods = ["GET", "POST"])
@ login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@ app.route("/history")
@ login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@ app.route("/login", methods = ["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows=db.execute("SELECT * FROM users WHERE username = :username",
                          username = request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"]=rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        flash("Existing users login")
        return render_template("login.html")


@ app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged out successfully.")
    return redirect("/")


@ app.route("/quote", methods = ["GET", "POST"])
@ login_required
def quote():
    """Get stock quote."""
    quote_details = ""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Fetch share details with API lookup
        quote_details = lookup(request.form.get("symbol"))
        if quote_details == None:
            return apology("invalid symbol", 403)
        else:
            quote_details["price"] = usd(quote_details["price"])
            return render_template("quote.html", quote_details=quote_details)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html", quote_details=quote_details)


@ app.route("/register", methods = ["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirm password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Query database for username to check if already exists
        rows=db.execute("SELECT * FROM users WHERE username = :username",
                          username = request.form.get("username"))
        if len(rows) > 0:
            flash("Username not available")
            return apology("select another username", 403)

        # Insert new user into DB, returns user ID
        session["user_id"]=db.execute("INSERT INTO users(username, hash) \
            VALUES(:username, :hashval)", username = request.form.get("username"),
                                        hashval = generate_password_hash(request.form.get("password")))

        # Login and Redirect user to home page
        flash("Welcome! You're registered now.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        flash("Register as a New User")
        return render_template("register.html")


@ app.route("/sell", methods = ["GET", "POST"])
@ login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e=InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    app.run(debug = True)
