from flask import Flask, render_template, request, url_for, redirect, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, Email, DataRequired
from flask_bcrypt import Bcrypt
from dash_app import visualisations
from data_filtering import get_website_info, get_circuit_name, get_page_name, get_possible_winners, is_wet_race, get_team_wins, is_red_flag, is_safety_car

app = Flask(__name__)

with app.app_context():
    g.cur_app = app

    app = visualisations.init_app("/visualisations/")



# add mysql db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:fortheproject24#@localhost:3306/users"
# secret key
app.config['SECRET_KEY'] = "asecretkey"
# initialise db
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# helps w/ loading users from ids

login_manager = LoginManager(app)

login_manager.login_view = "login"

# (load_user/user id desc)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# creates table for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    reviews = db.relationship('Review', backref='user')
    ratings = db.relationship('Rating', backref='user')
    replies = db.relationship('Reply', backref='user')
    watchlists = db.relationship('Watchlist', backref='user')


# creates table for reviews
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(360), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    circuit = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    replies = db.relationship('Reply', backref='review')

    def __repr__(self) -> str:
        return f"Review {self.id}"

# creates table for ratings
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratingNum =  year = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    circuit = db.Column(db.String(20), nullable=False)

# creates table for replies
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'))
    content = db.Column(db.String(360), nullable=False)
    username = db.Column(db.String(20), nullable=False)

# creates table for watchlists
class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    contents = db.relationship('WatchlistContent', backref='watchlist')


# creates table for the contents of watchlists
class WatchlistContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'))
    year = db.Column(db.Integer)
    circuit = db.Column(db.String(20))


# class for 'race' table
class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(20))
    circuit = db.Column(db.String(20))
    winner_name = db.Column(db.String(30))
    team = db.Column(db.String(40))
    wet_race = db.Column(db.Boolean)
    red_flag = db.Column(db.Boolean)
    safety_car = db.Column(db.Boolean)
    year = db.Column(db.Integer)

# Register form

class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Password"})

    email = EmailField(validators=[InputRequired(), Email(), Length(min=10, max=40)], render_kw={"placeholder":"Email Address"})

    submit = SubmitField("Sign up")

    # checks whether username hasn't already been used

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()

        if existing_username:
            raise ValidationError("That username is already being used - Please choose a different one.")
    
    # checks whether email has already been used 

    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()

        if existing_email:
            raise ValidationError("This email address is already connected to an account!")    

#creates login form

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Log in")

class ReviewForm(FlaskForm):
    content = TextAreaField(validators=[InputRequired(), Length(min=5, max=360)], render_kw={"placeholder" : "Add a review..."})

    review_submit = SubmitField("Post Review")

# creates rating form

class RatingForm(FlaskForm):

    rating = RadioField('Rate this race: ', validators=[InputRequired()],
                        choices= [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    rating_submit = SubmitField("Submit Rating")

# creates reply form
class ReplyForm(FlaskForm):
    content = TextAreaField(validators=[InputRequired(), Length(min=5, max=360)], render_kw={"placeholder" : "Add a reply..."})

    reply_submit = SubmitField("Post Reply")

# creates watchlist form
class WatchlistForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder":"Name your watchlist"})

    wl_submit = SubmitField("Create Watchlist")

# creates submit button for watchlist contents
class WatchlistContentsForm(FlaskForm):
    content_submit = SubmitField("Add to watchlist")

# creates a form to retrieve searched text / filter results
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    dr_winner = SelectField("Filter by race winner", choices=[("All", "All"), ("Max Verstappen", "Max Verstappen"), ("Sergio Perez", "Sergio Perez"), ("Carlos Sainz", "Carlos Sainz"), ("Lando Norris", "Lando Norris"), 
                                                             ("Charles Leclerc", "Charles Leclerc"), ("George Russell", "George Russell"), ("Lewis Hamilton", "Lewis Hamilton"), ("Oscar Piastri", "Oscar Piastri")])
    team_winner = SelectField("Filter by winning team", choices=[("All", "All"), ("Red Bull Racing Honda RBPT", "Red Bull Racing Honda RBPT"), 
                                                                 ("Ferrari", "Ferrari"), ("Mercedes", "Mercedes"), ("McLaren Mercedes", "McLaren Mercedes"), ("McLaren", "McLaren"), ("Red Bull Racing", "Red Bull Racing")])
    conditions = SelectField("Filter by race conditions", choices=[("All", "All"), ("Wet/Mixed", "Wet/Mixed"), ("Dry", "Dry")])
    years = SelectField("Filter by race conditions", choices=[("All", "All"), ("2023", "2023"), ("2024", "2024"), ("2025", "2025"), ("2026", "2026")])
    search_submit = SubmitField("Submit")



# START OF ROUTES
# home page route

@app.route('/')
def home():
    return render_template('home.html')

# route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        l_user = User.query.filter_by(username=form.username.data).first()
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
        newUser = User(username=form.username.data, password=hashed_pw, email=form.email.data)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

# logs out user
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# redirects user to their user page if login is successful
@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    wl_form = WatchlistForm()

    if request.method == "POST":
        if wl_form.wl_submit.data and wl_form.validate():
            new_watchlist = Watchlist(name=wl_form.name.data, user_id = current_user.id)
            try:
                db.session.add(new_watchlist)
                db.session.commit()
                return redirect('/user_dashboard')
            except Exception as e:
                print(f"Error: {e}")
                return f"Error:{e}"
    
    else:
        watchlists = Watchlist.query.filter_by(user_id = current_user.id).all()
        return render_template('user_dashboard.html', wl_form = wl_form, watchlists = watchlists)


#route for watchlist page
@app.route('/watchlist/<int:id>', methods=["GET", "POST"])
@login_required
def watchlist(id:int):
    if request.method == "POST":
        return redirect(f'/watchlist/{id}')
    else:
        contents = WatchlistContent.query.filter_by(watchlist_id = id).all()
        wlist = Watchlist.query.filter_by(id = id).first()
        return render_template('watchlist.html', contents = contents, wlist = wlist)


#created by following this tutorial: https://www.youtube.com/watch?v=kmtZTo-_gJY

# pass form to other pages
@app.context_processor
def base():
    s_form = SearchForm()
    return dict(s_form = s_form)


@app.route('/search')
def search():
    return render_template("search.html")


# handles search results
@app.route('/search_results', methods=["POST"])
def search_results():
    s_form = SearchForm()
    races = Race.query
    if s_form.validate_on_submit():
        
        # gets data from form
        race_searched = s_form.searched.data
        winner_dr = s_form.dr_winner.data
        win_team = s_form.team_winner.data
        condition = s_form.conditions.data
        year = s_form.years.data


        # searches database for data that matches search
        races = races.filter(Race.country.like('%' + race_searched + '%'))

        # check if any filters have been chosen - if that is the case, filter the list of races accordingly
        if (winner_dr != "All"):
            races = races.filter(Race.winner_name == winner_dr)

        if (win_team != "All"):
            races = races.filter(Race.team == win_team)

        if (condition == "Wet/Mixed"):
            races = races.filter(Race.wet_race == 1)
        elif (condition == "Dry"):
            races = races.filter(Race.wet_race == 0)

        if (year != "All"):
            races = races.filter(Race.year == int(year))

        races = races.order_by(Race.year).all()
        return render_template("search_results.html", s_form=s_form, searched = race_searched, races=races, winner = winner_dr, team = win_team, condition = condition, year=year)



# function to redirect users to the page of the race that they have added to their watchlist
@app.route('/view_race/<season>/<race>', methods=["GET", "POST"])
@login_required
def get_race(season, race):
    page = get_page_name(season, race)

    season = str(season)

    return add_page_contents(season, page)



# route for seasons page
@app.route('/seasons')
@login_required
def seasons():
    return render_template('seasons.html')

# route for all race pages
@app.route('/all_seasons/<season>/<race>', methods=['GET', 'POST'])
@login_required
# function that both handles the POST requests from the multiple forms in these pages,
# and returns information that will be displayed on the pages

def add_page_contents(season, race):
    # code snippet taken from https://www.youtube.com/watch?v=45P3xQPaYxc&t=2388s , edited to fit with my project
    # start of adjusted code snippet

    circuit_name = get_circuit_name(race)
    year = int(season)
    form1 = RatingForm()
    form2 = ReviewForm()
    form_reply = ReplyForm()
    list_contents = WatchlistContentsForm()

    if request.method == "POST":

        # add a review
        if form2.review_submit.data and form2.validate():
            new_review = Review(content=form2.content.data, year=year, circuit=circuit_name, user_id = current_user.id, username = current_user.username)
            try:
                db.session.add(new_review)
                db.session.commit()
                return redirect(f"/all_seasons/{season}/{race}")
            except Exception as e:
                print(f"Error: {e}")
                return f"Error:{e}"
        
        # solution for dealing with multiple forms in one page (following if statement) from stack overflow: https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms 
        elif form1.rating_submit.data and form1.validate():
            rating = int(form1.rating.data)
            new_rating = Rating(user_id = current_user.id, ratingNum = rating, year = year, circuit =  circuit_name)
            try:
                db.session.add(new_rating)
                db.session.commit()
                return redirect(f"/all_seasons/{season}/{race}")
            except Exception as e:
                print(f"Error: {e}")
                return f"Error:{e}"
        
        

    else:
        avg_rating = get_avg_rating(year, circuit_name)
        personal_rating = Rating.query.filter_by(year=year, circuit=circuit_name, user_id = current_user.id).first()
        personal_review = Review.query.filter_by(user_id = current_user.id, year = year, circuit = circuit_name).first()
        reviews = Review.query.filter_by(year=year, circuit=circuit_name).all()
        replies = Reply.query.all()
        web_info = get_website_info(year, circuit_name)
        past_wins = get_possible_winners(circuit_name)
        constructors = get_team_wins(circuit_name)
        wet_races = is_wet_race(circuit_name)
        sc = is_safety_car(circuit_name)
        red_flag = is_red_flag(circuit_name)
        watchlists = Watchlist.query.filter_by(user_id = current_user.id).all()
        listed = WatchlistContent.query.filter_by(year = year, circuit = circuit_name).all()
        all_ids = []

        for list in listed:
            all_ids.append(list.watchlist_id)


        # else:
        return render_template(f'all_seasons/{season}/{race}.html', reviews=reviews, replies=replies, web_info=web_info, personal_rating=personal_rating, 
                        personal_review = personal_review, avg_rating = avg_rating, form1=form1, form2=form2, form_reply=form_reply, watchlists = watchlists, list_contents = list_contents,
                        listed = listed, all_ids = all_ids, past_wins = past_wins, constructors = constructors, wet_races = wet_races, sc = sc, red_flag=red_flag)


# delete a review
@app.route("/delete/<int:id>")
def delete_review(id:int):
    del_review = Review.query.get_or_404(id)
    del_replies = Reply.query.filter_by(review_id = id).all()
    try:
        if del_replies != None:
            for reply in del_replies:
                db.session.delete(reply)
        db.session.delete(del_review)
        db.session.commit()
        # came across an error regarding redirecting to the current page, fixed it below with a line of code from https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
        return redirect(request.referrer)
    except Exception as e:
        return f"Error:{e}"
    
# end of adjusted code snippet

@app.route("/delete_rating/<int:id>")
def delete_rating(id:int):
    del_rating = Rating.query.get_or_404(id)
    try:
        db.session.delete(del_rating)
        db.session.commit()
        # came across an error regarding redirecting to the current page, fixed it below with a line of code from https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
        return redirect(request.referrer)
    except Exception as e:
        return f"Error:{e}"

# function for adding a reply
@app.route("/post_reply/<int:id>", methods=["POST"])
def post_reply(id:int):
    form_reply = ReplyForm()
    if request.method == "POST":
        new_reply = Reply(user_id = current_user.id, review_id = id, content = form_reply.content.data, username = current_user.username)
        try:
            db.session.add(new_reply)
            db.session.commit()
            return redirect(request.referrer)
        except Exception as e:
            print(f"Error: {e}")
            return f"Error:{e}"

# function for deleting a reply
@app.route("/delete_reply/<int:id>")
def delete_reply(id:int):
    delete_reply = Reply.query.get_or_404(id)
    try:
        db.session.delete(delete_reply)
        db.session.commit()
        # came across an error regarding redirecting to the current page, fixed it below with a line of code from https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
        return redirect(request.referrer)
    except Exception as e:
        return f"Error:{e}"


# function for deleting a watchlist
@app.route("/delete_wl/<int:id>")
def delete_wl(id:int):
    delete_wl = Watchlist.query.get_or_404(id)
    try:
        db.session.delete(delete_wl)
        db.session.commit()
        # came across an error regarding redirecting to the current page, fixed it below with a line of code from https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
        return redirect('/user_dashboard')
    except Exception as e:
        return f"Error:{e}"


# function for adding a race to a watchlist
@app.route("/all_seasons/<season>/<race>/add_race/<int:id>", methods=["GET", "POST"])
def add_to_list(season, race, id:int):
    list_contents = WatchlistContentsForm()
    circuit_name = get_circuit_name(race)
    year = int(season)

    if request.method == "POST":
        added_race = WatchlistContent(watchlist_id = id, year = year, circuit = circuit_name)
        try:
            db.session.add(added_race)
            db.session.commit()
            return redirect(f"/all_seasons/{season}/{race}")
        except Exception as e:
            print(f"Error: {e}")
            return f"Error:{e}"
    else:
        return redirect(f"/all_seasons/{season}/{race}", list_contents = list_contents)


# function for deleting a race from a watchlist
@app.route("/delete_from_list/<int:id>")
def delete_from_list(id:int):
    del_race = WatchlistContent.query.get_or_404(id)

    try:
        db.session.delete(del_race)
        db.session.commit()
        # came across an error regarding redirecting to the current page, fixed it below with a line of code from https://stackoverflow.com/questions/41270855/flask-redirect-to-same-page-after-form-submission
        return redirect(request.referrer)
    except Exception as e:
        return f"Error:{e}"



# function to calculate mean of all ratings given to a race
def get_avg_rating(year, circuit):
    race_ratings = Rating.query.filter_by(year=year, circuit=circuit).with_entities(Rating.ratingNum).all()

    # divide by length of list
    rating_len = len(race_ratings)

    # if no ratings have been submitted yet
    if rating_len == 0:
        return 0
    
    total = 0

    for users_rating in race_ratings:
        for rating in users_rating:
            total += rating
    
    mean = total / rating_len

    return mean


# only uncomment the commented code below if you would like to recreate the needed tables in your own database
if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)

