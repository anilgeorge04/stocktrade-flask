# FIT INVESTORS
## Train to Trade 

A real-time practice ground for trading* in any listed US stock.

The best way to learn is by doing. The **FIT INVESTORS** simulation helps you buy and sell shares, and manage a stock portfolio*.  Seasoned investors can use **FIT INVESTORS** as their sandbox account to make experimental bets with their portfolio. For investors new to stock investing, it prepares you first hand for the movements of a stock market.

*NO real money involved. Designed purely for hands-on learning and practice. Uses US Stocks data provided by IEX.
No email required to explore and use the app. Your password is hashed. But, use any available dummy username and password. Preferably one that you don't use for anything else.

## How do I get started?
- Register as a new user or Login as an existing user
- Start off with $10,000 as "cash balance"
- Find quotes of the stocks you are interested in real-time
- Buy shares with your cash balance, sell shares and manage your portfolio
- View your transaction history under your account

All the best!

---
### About the App
Light-weight web application built using Python's Flask web framework and hosted on Heroku. Uses Bootstrap components and JavaScript. The application performs CRUD operations using SQLite3 as the persistence layer. US stock quotes are fetched using APIs from IEX.

### For Developers
1. Clone the repository
2. Create an empty "finance.db" file and run manage.py to initialize it as a SQLite database with "users" and "purchases" tables. You can alter the default cash balance here (currently set to $10,000).
3. Register at [IEX](https://www.iexcloud.io/) and get a token for your API calls to fetch Stock Data from IEX. More details about API [here](https://iexcloud.io/docs/api/). 
4. Export the API KEY in your environment before running the Flask App. Example: `export API_KEY=<token>`
5. Run the flask app with `flask run`

#### Note
It is not advisable to use Sqlite3 on a Production server with Session Type as "filesystem" as shown in this app. Heroku uses an ephemeral filesystem. This project was created to explore Flask in detail and the ability to run CRUD operations and work closely with a SQL persistence layer, which works great on Flask's Development server. It is advised to use PostgreSQL with Heroku for Production.