"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True, default=None)
    password = db.Column(db.String(64), nullable=True, default=None)
    age = db.Column(db.Integer, nullable=True, default=None)
    zipcode = db.Column(db.String(15), nullable=True, default=None)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append((u_r.score, r.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict a user's rating of a movie."""

        other_ratings = movie.ratings

        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        similarities.sort(reverse=True)
        similarities = [(sim, r) for sim, r in similarities if sim > 0]
        if not similarities:
            return None
        numerator = sum([r.score * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator / denominator

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s password=%s age=%s, zipcode=%s>" % (self.user_id,
                                                                              self.email,
                                                                              self.password,
                                                                              self.age,
                                                                              self.zipcode)

# Put your Movie and Rating model classes here.


class Movie(db.Model):
    """Information about movies in our database."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(500), nullable=True, default=None)
    released_at = db.Column(db.Date, nullable=True, default=None)
    imdb_url = db.Column(db.String(500), nullable=True, default=None)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User movie_id=%s title=%s released_at=%s imdb_url=%s>" % (self.movie_id,
                                                                           self.title,
                                                                           self.released_at,
                                                                           self.imdb_url)


class Rating(db.Model):
    """Information about ratings in our database."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=True, default=None)

    user = db.relationship("User", backref="ratings", order_by=rating_id)
    movie = db.relationship("Movie", backref="ratings", order_by=rating_id)

    @classmethod
    def new_rating(cls, movie_id, user_id, score):
        """insert new rating"""
        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=score)
        db.session.add(rating)
        db.session.commit()


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User rating_id=%s movie_id=%s user_id=%s score=%s>" % (self.rating_id,
                                                                        self.movie_id,
                                                                        self.user_id,
                                                                        self.score)

##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
