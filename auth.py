from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from flask_login import UserMixin


app = Flask(__name__)

engine = sa.create_engine("mysql+pymysql://root:fortheproject24#@localhost:3306/users", echo=True)

meta = sa.MetaData()
#db = SQLAlchemy()
# add mysql db
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:fortheproject24#@localhost:3306/root$users"
# secret key
#app.config['SECRET_KEY'] = "asecretkey"
# initialise db
#db.init_app(app)

# metadata user table?

user = sa.Table(
    "user",
    meta,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(20), nullable=False, unique=True),
    sa.Column("password", sa.String(80), nullable=False),
    sa.Column("email", sa.String(40), nullable=False, unique=True)

)

meta.create_all(engine)

conn = engine.connect()



# creates table for users
#class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(20), nullable=False, unique=True)
#    password = db.Column(db.String(80), nullable=False)
#    email = db.Column(db.String(40), nullable=False, unique=True)


# first page to show up, maybe edit so that it's the login page instead?
@app.route('/')
def home():
    return render_template('home.html')

# route to login page
@app.route('/login')
def login():
    return render_template('login.html')

# route to sign up page
@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)

