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


@ app.route("/")
@ login_required
def index():
    """Show portfolio of stocks"""

    # user's portfolio by stock symbol
    portfolio = db.execute(
        "SELECT symbol, SUM(shares) AS shares FROM purchases WHERE user_id = :user_id GROUP BY(symbol) HAVING SUM(shares) > 0",
        user_id=session["user_id"])
    # current cash & overall portfolio value
    cash_row = db.execute(
        "SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    balance = cash_row[0]["cash"]
    overall = balance

    # Dynamic fetch Company Name and Current Share Price
    for sym in portfolio:
        quote_details = lookup(sym["symbol"])
        sym["name"] = quote_details["name"]
        sym["price"] = quote_details["price"]
        sym["total"] = sym["price"] * sym["shares"]
        overall += sym["total"]

    return render_template("index.html", portfolio=portfolio, balance=balance, overall=overall, username=session["username"], )


@ app.route("/buy", methods=["GET", "POST"])
@ login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol and shares was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        elif not request.form.get("shares"):
            return apology("must provide number of shares", 400)
        shares = int(request.form.get("shares"))

        # Fetch share details with API lookup
        quote_details = lookup(request.form.get("symbol"))
        if quote_details == None:
            flash("Invalid symbol!")
            return redirect("/buy")
        else:
            price = quote_details["price"]
            cash_row = db.execute(
                "SELECT cash FROM users WHERE id=:id", id=session["user_id"])
            cash = cash_row[0]["cash"]
            cash = cash - (price*shares)
            if cash < 0:
                flash(f"Sorry! You are short by ${-cash:} to make this purchase.")
                return redirect("/buy")
            else:
                db.execute("UPDATE users SET cash=:cash WHERE id=:id",
                           cash=cash, id=session["user_id"])
                db.execute("INSERT INTO purchases(symbol, shares, price, user_id) \
                    VALUES(:symbol, :shares, :price, :user_id)",
                           symbol=quote_details["symbol"], shares=shares, price=price, user_id=session["user_id"])
                flash("Success: Purchased stock and debited cash")
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@ app.route("/history")
@ login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol, shares, price, transacted_on FROM purchases \
        WHERE user_id=:user_id", user_id=session["user_id"])
    return render_template("history.html", transactions=transactions)


@ app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please provide username and password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password.")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@ app.route("/changepwd", methods=["GET", "POST"])
@ login_required
def changepwd():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        def provide_check(field):
            if not request.form.get(field):
                return f"Please provide {field}"
            else:
                return None

        # Ensure old & new password and confirmation was submitted
        result_check = provide_check("oldpassword") or provide_check(
            "newpassword") or provide_check("confirmation")
        if result_check is not None:
            flash(result_check)
            return render_template("changepwd.html")

        # Ensure new password and confirmation match
        elif not request.form.get("newpassword") == request.form.get("confirmation"):
            flash("New password and confirmation do not match. Try again.")
            return render_template("changepwd.html")

        # -- until above, all checks performed within HTML and JS --
        # placed above for redundancy when JavaScript is disabled

        # Ensure new password is different from old password
        elif request.form.get("oldpassword") == request.form.get("newpassword"):
            flash("New password can't be same as old password. Try again.")
            return render_template("changepwd.html")

        # Check if old password is valid
        oldhash = db.execute("SELECT hash FROM users WHERE id = :id",
                             id=session["user_id"])
        if not check_password_hash(oldhash[0]["hash"], request.form.get("oldpassword")):
            flash("Unsuccessful: Invalid old password")
            return render_template("changepwd.html")

        # Update password in DB
        db.execute("UPDATE users SET hash=:hashval WHERE id=:id",
                   id=session["user_id"], hashval=generate_password_hash(request.form.get("newpassword")))

        # Login and Redirect user to home page
        flash("Password changed successfully!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        flash("Choose a new password")
        return render_template("changepwd.html")


@ app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged out successfully.")
    return redirect("/")


@ app.route("/quote", methods=["GET", "POST"])
@ login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("symbol"):
            flash("Please provide Stock Symbol")
            return render_template("quote.html", quoteDetails=None)

        # Fetch share details with API lookup
        quote_details = lookup(request.form.get("symbol"))
        if quote_details == None:
            flash("Invalid Symbol")
        else:
            flash("Details fetched successfully")
        return render_template("quote.html", quote_details=quote_details)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html",  quote_details=None)


@ app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username, password and confirmation was submitted
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("Please fill all required fields")
            return render_template("register.html")

        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("New password and Confirmation do not match. Try again.")
            return render_template("register.html")

        # Query database for username to check if already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        if len(rows) > 0:
            flash("Username not available. Try another one.")
            return render_template("register.html")

        # Insert new user into DB, returns user ID
        session["user_id"] = db.execute("INSERT INTO users(username, hash) \
            VALUES(:username, :hashval)", username=request.form.get("username"),
                                        hashval=generate_password_hash(request.form.get("password")))

        # Login and Redirect user to home page
        flash("Welcome! You're registered now.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        flash("Register as a New User")
        return render_template("register.html")


@ app.route("/sell", methods=["GET", "POST"])
@ login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol and shares was submitted (HTML does this check too)
        symbol_request = request.form.get("symbol")
        if not symbol_request or not request.form.get("shares"):
            flash("Please provide symbol and number of shares")
            return redirect("/sell")
        shares_request = int(request.form.get("shares"))

        # Fetch share details with API lookup
        quote_details = lookup(symbol_request)
        if quote_details == None:
            flash("Invalid symbol. Check and try again.")
            return redirect("/sell")
        else:
            share_row = db.execute("SELECT SUM(shares) AS shares FROM purchases \
                WHERE user_id=:user_id GROUP BY(symbol) HAVING symbol=:symbol",
                                   user_id=session["user_id"], symbol=quote_details["symbol"])
            shares_held = share_row[0]["shares"]
            if shares_held < shares_request:
                flash(f"Sorry! You only have {shares_held:} share(s) of {symbol_request:}. \
                    Cannot sell {shares_request:} share(s).")
                return redirect("/sell")
            else:
                price = quote_details["price"]
                cash_row = db.execute(
                    "SELECT cash FROM users WHERE id=:id", id=session["user_id"])
                cash = cash_row[0]["cash"]
                cash = cash + (price*shares_request)
                db.execute("UPDATE users SET cash=:cash WHERE id=:id",
                           cash=cash, id=session["user_id"])
                db.execute("INSERT INTO purchases(symbol, shares, price, user_id) \
                    VALUES(:symbol, -:shares, :price, :user_id)",
                           symbol=quote_details["symbol"], shares=shares_request, price=price, user_id=session["user_id"])
                flash("Success: Stock sold and cash credited")
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        stocks = db.execute(
            "SELECT symbol FROM purchases WHERE user_id=:user_id GROUP BY(symbol) HAVING SUM(shares) > 0", user_id=session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    app.run(debug=True)
