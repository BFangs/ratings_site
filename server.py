"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    a = jsonify([1,3])
    return render_template("homepage.html")


@app.route("/movies")
def movie_list():
    """Show list of movie titles."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>", methods=['GET'])
def movie_info(movie_id):
    """Show movie and the ratings for that movie."""

    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    return render_template(
        "movie_info.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction
        )


@app.route("/rate", methods=['POST'])
def rate_movie():
    """Insert ratings for that one movie."""

    rating = int(request.form.get("rate"))
    movie = request.form.get("movie_id")
    user_id = session["user_id"]
    try:
        old_rating = Rating.query.filter_by(movie_id=movie, user_id=user_id).one()
        old_rating.score = rating
        db.session.commit()
        flash("You've already rated it! I've gone ahead and updated your rating dum dum")
    except:
        Rating.new_rating(movie, user_id, rating)
        flash("You've made a new rating!")
    return redirect("/users/%s" % (user_id))


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.order_by('user_id').all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def user_info(user_id):
    """Show details about a user and movies they've reviewed."""

    person = User.query.filter_by(user_id=user_id).one()
    return render_template("user_info.html",
                           user=person)


@app.route("/register")
def register_form():
    """Registration form for ratings site."""

    return render_template("register_form.html")


@app.route("/register", methods=['POST'])
def register_process():
    """Accept or reject email address and password by checking if user exists."""

    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(email=username).all():
        flash("You've already made an account dum dum!")
        return redirect("/login")
        # if User.query.filter_by(password=password).all():
        #     response = {'username': username, 'password': password}
        #     return jsonify(response)
        # else:
        #     response = {'username': username}
        #     return jsonify(response)
    else:
        user = User(email=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")


@app.route("/login")
def login():
    """Display login form for already registered users."""
    return render_template("login_form.html")


@app.route("/login", methods=['POST'])
def login_process():
    """Check that email and password match or if email exists."""

    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(email=username).all():
        user = User.query.filter_by(email=username).one()
        if user.password == password:
            session["user_id"] = user.user_id
            flash("You're now logged in! Congrats!")
            return redirect("/users/%s" % (user.user_id))
        else:
            flash("That was the wrong password dum dum!!")
            return redirect("/login")
    else:
        flash("You haven't made an account yet! Register now!")
        return redirect("/register")


@app.route("/loggout")
def loggout():
    """Link to delete user session/log user out of ratings site."""
    del session["user_id"]
    flash("You're now logged out")
    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
