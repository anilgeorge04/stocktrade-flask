# To build the database for first run
from cs50 import SQL

db = SQL("sqlite:///finance.db")

# Users Table
# Start users with default $10000 balance
db.execute("CREATE TABLE 'users' \
    ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
        'username' TEXT NOT NULL, \
            'hash' TEXT NOT NULL, \
                'cash' NUMERIC NOT NULL DEFAULT 10000.00)")

# Purchases Table
db.execute("CREATE TABLE 'purchases' \
    ('txn_id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
        'symbol' TEXT NOT NULL, \
            'shares' NUMERIC NOT NULL,\
                'price' NUMERIC NOT NULL, \
                    transacted_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                        user_id INTEGER NOT NULL, \
                            FOREIGN KEY(user_id) REFERENCES users(id))")