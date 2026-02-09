from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
#import sqlalchemy as sa
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# FYI THIS FIXES THE CREATE TABLES ISSUE
# from auth import app, db
# db.init_app(app) 
# app.app_context().push()
# db.create_all()
# exit()

#engine = sa.create_engine("mysql+pymysql://root:fortheproject24#@localhost:3306/users", echo=True)

#meta = sa.MetaData()
# add mysql db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:fortheproject24#@localhost:3306/users"
# secret key
app.config['SECRET_KEY'] = "asecretkey"
# initialise db
db = SQLAlchemy(app)
#db.init_app(app)
bcrypt = Bcrypt(app)

# helps w/ loading users from ids

login_manager = LoginManager(app)
#login_manager.init.app(app)
login_manager.login_view = "login"

# (load_user/user id desc)

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

# metadata user table?

#user = sa.Table(
#    "user",
#    meta,
#    sa.Column("id", sa.Integer, primary_key=True),
#    sa.Column("username", sa.String(20), nullable=False, unique=True),
#    sa.Column("password", sa.String(80), nullable=False),
#    sa.Column("email", sa.String(40), nullable=False, unique=True)
#
#)

#meta.create_all(engine)

#conn = engine.connect()


# creates table for users
class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)


# Register form

class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Password"})

    email = EmailField(validators=[InputRequired(), Email(), Length(min=10, max=40)], render_kw={"placeholder":"Email Address"})

    submit = SubmitField("Sign up")

    # checks whether username hasn't already been used

    def validate_username(self, username):
        existing_username = user.query.filter_by(username=username.data).first()

        if existing_username:
            raise ValidationError("That username is already being used - Please choose a different one.")
    
    # checks whether email has already been used 

    def validate_email(self, email):
        existing_email = user.query.filter_by(email=email.data).first()

        if existing_email:
            raise ValidationError("This email address is already connected to an account!")    

#creates login form

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Log in")


# first page to show up, maybe edit so that it's the login page instead?
@app.route('/')
def home():
    return render_template('home.html')

# route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        l_user = user.query.filter_by(username=form.username.data).first()
        if l_user:
            if bcrypt.check_password_hash(l_user.password, form.password.data):
                login_user(l_user)
                return redirect(url_for('user_dashboard'))

    return render_template('login.html', form=form)

# route to sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        newUser = user(username=form.username.data, password=hashed_pw, email=form.email.data)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

# redirects user to their user page if login is successful
@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')

# logs out user
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

