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


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def user_info(user_id):
    """Show list of users."""

    person = User.query.filter_by(user_id=user_id).one()
    return render_template("user_info.html",
                            user=person)

@app.route("/register")
def register_form():

    return render_template("register_form.html")


@app.route("/register", methods=['POST'])
def register_process():

    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(email=username).all():
        flash("You've already made an account dum dum!")
    else:
        user = User(email=username, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")

@app.route("/login")
def login():

    return render_template("login_form.html")


@app.route("/login", methods=['POST'])
def login_process():

    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(email=username).all():
        user = User.query.filter_by(email=username).one()
        if user.password == password:
            session["user_id"] = user.user_id
            flash("You're now logged in! Congrats!")
        else:
            flash("That was the wrong password dum dum!!")
            return redirect("/login")
    else:
        flash("You haven't made an account yet! Register now!")
        return redirect("/register")

    return redirect("/")

@app.route("/loggout")
def loggout():
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
