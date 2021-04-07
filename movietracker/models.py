import click
from flask.cli import with_appcontext
from movietracker import db
from movietracker.utils import get_uuid

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie-tracker.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)


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

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["title"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Movie name",
            "type": "string"
        }
        props["actors"] =  {
            "description": "Actors on the movie",
            "type": "string"
        }
        props["release_date"] =  {
            "description": "Release date of the movie",
            "type": "string",
            "pattern": "^[0-3][0-9]-[01][0-9]-[0-9]{4}$"
        }
        props["score"] = {
            "description": "IMDb score of the movie",
            "type": "number"
        }
        return schema


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

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["title", "seasons"],
            "additionalProperties": False
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Series name",
            "type": "string"
        }
        props["actors"] =  {
            "description": "Actors on the series",
            "type": "string"
        }
        props["release_date"] =  {
            "description": "Release date of the series",
            "type": "string",
            "pattern": "^[0-3][0-9]-[01][0-9]-[0-9]{4}$"
        }
        props["score"] = {
            "description": "IMDb score of the series",
            "type": "number"
        }
        props["seasons"] = {
            "description": "Number of seasons",
            "type": "number"
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
    genres = ["action", "crime", "romance", "drama", "horror", "fantasy"]
    for g in genres:
        db.session.add(Genre(name=g))
    db.session.commit()

    db.session.add(Movie(
        title="The Avengers",
        uuid=get_uuid(),
        actors="Robert Downey Jr.",
        release_date="11-04-2012",
        score=8.0,
        genre=Genre.query.filter_by(name="action").first()
    ))
    db.session.add(Movie(
        title="Sherlock Holmes",
        uuid=get_uuid(),
        actors="Robert Downey Jr.",
        release_date="25-12-2009",
        score=8.0,
        genre=Genre.query.filter_by(name="crime").first()
    ))

    db.session.add(Series(
            title="Breaking Bad",
            actors="Bryan Cranston",
            uuid=get_uuid(),
            release_date="20-01-2008",
            score=9.5,
            seasons=5,
            genre=Genre.query.filter_by(name="crime").first()
    ))
    db.session.add(Series(
            title="Game of Thrones",
            uuid=get_uuid(),
            actors="Emilia Clarke, Kit Harrington",
            release_date="17-04-2011",
            score=9.5,
            seasons=8,
            genre=Genre.query.filter_by(name="fantasy").first()
    ))
    db.session.commit()