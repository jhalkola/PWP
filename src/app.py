from enum import unique
import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    movies = db.relationship("Movie", back_populates="genre")
    series = db.relationship("Series", back_populates="genre")

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"))
    title = db.Column(db.String(64), nullable=False)
    uuid = db.Column(db.String(64), nullable=False, unique=True)
    actors = db.Column(db.String(64), nullable=True)
    release_date = db.Column(db.String(64), nullable=True)
    score = db.Column(db.Float, nullable=True)

    genre = db.relationship("Genre", back_populates="movies")

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"))
    title = db.Column(db.String(64), nullable=False)
    uuid = db.Column(db.String(64), nullable=False, unique=True)
    actors = db.Column(db.String(64), nullable=True)
    release_date = db.Column(db.String(64), nullable=True)
    score = db.Column(db.Float, nullable=True)
    seasons = db.Column(db.Integer, default=1, nullable=False)

    genre = db.relationship("Genre", back_populates="series")