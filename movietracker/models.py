import click
from flask.cli import with_appcontext
from movietracker import db
from movietracker.utils import get_uuid

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
    release_date = db.Column(db.String(64), nullable=False)
    score = db.Column(db.Float, nullable=True)

    genre = db.relationship("Genre", back_populates="movies")

    @staticmethod
    def get_schema_post():
        schema = {
            "type": "object",
            "required": ["title", "release_date"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Movie name",
            "type": "string",
            "minLength": 1
        }
        props["actors"] =  {
            "description": "Actors on the movie",
            "type": ["string", "null"]
        }
        props["release_date"] =  {
            "description": "Release date of the movie",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
        }
        props["score"] = {
            "description": "IMDb score of the movie",
            "type": ["number", "null"]
        }
        return schema

    @staticmethod
    def get_schema_put():
        schema = {
            "type": "object",
            "required": ["title", "release_date", "genre"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Movie name",
            "type": "string",
            "minLength": 1
        }
        props["actors"] =  {
            "description": "Actors on the movie",
            "type": ["string", "null"]
        }
        props["release_date"] =  {
            "description": "Release date of the movie",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
        }
        props["score"] = {
            "description": "IMDb score of the movie",
            "type": ["number", "null"]
        }
        props["genre"] = {
            "description": "Genre of the movie",
            "type": "string"
        }
        return schema


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"))
    title = db.Column(db.String(64), nullable=False)
    uuid = db.Column(db.String(64), nullable=False, unique=True)
    actors = db.Column(db.String(64), nullable=True)
    release_date = db.Column(db.String(64), nullable=False)
    score = db.Column(db.Float, nullable=True)
    seasons = db.Column(db.Integer, default=1, nullable=False)

    genre = db.relationship("Genre", back_populates="series")

    @staticmethod
    def get_schema_post():
        schema = {
            "type": "object",
            "required": ["title", "release_date", "seasons"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Series name",
            "type": "string",
            "minLength": 1
        }
        props["actors"] =  {
            "description": "Actors on the series",
            "type": ["string", "null"]
        }
        props["release_date"] =  {
            "description": "Release date of the series",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
        }
        props["score"] = {
            "description": "IMDb score of the series",
            "type": ["number", "null"]
        }
        props["seasons"] = {
            "description": "Number of seasons",
            "type": "integer"
        }
        return schema

    @staticmethod
    def get_schema_put():
        schema = {
            "type": "object",
            "required": ["title", "release_date", "seasons", "genre"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Series name",
            "type": "string",
            "minLength": 1
        }
        props["actors"] =  {
            "description": "Actors on the series",
            "type": ["string", "null"]
        }
        props["release_date"] =  {
            "description": "Release date of the series",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
        }
        props["score"] = {
            "description": "IMDb score of the series",
            "type": ["number", "null"]
        }
        props["seasons"] = {
            "description": "Number of seasons",
            "type": "integer"
        }
        props["genre"] = {
            "description": "Genre of the series",
            "type": "string"
        }
        return schema


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

@click.command("testgen")
@with_appcontext
def generate_test_data():
    # add genres to test db
    genres = ["Action", "Crime", "Romance", "Drama", "Horror", "Fantasy"]
    for g in genres:
        db.session.add(Genre(name=g))
    db.session.commit()

    db.session.add(Movie(
        title="The Avengers",
        uuid=get_uuid(),
        actors="Robert Downey Jr.",
        release_date="2012-04-11",
        score=8.0,
        genre=Genre.query.filter_by(name="Action").first()
    ))
    db.session.add(Movie(
        title="Sherlock Holmes",
        uuid=get_uuid(),
        actors="Robert Downey Jr.",
        release_date="2009-12-25",
        genre=Genre.query.filter_by(name="Crime").first()
    ))

    db.session.add(Series(
            title="Breaking Bad",
            uuid=get_uuid(),
            release_date="2008-01-20",
            score=9.5,
            seasons=5,
            genre=Genre.query.filter_by(name="Crime").first()
    ))
    db.session.add(Series(
            title="Game of Thrones",
            uuid=get_uuid(),
            actors="Emilia Clarke, Kit Harrington",
            release_date="2011-04-17",
            score=9.5,
            seasons=8,
            genre=Genre.query.filter_by(name="Fantasy").first()
    ))
    db.session.commit()