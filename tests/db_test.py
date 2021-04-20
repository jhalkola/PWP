import os
import pytest
import tempfile
import shortuuid
from sqlalchemy.engine import Engine
from sqlalchemy import event
from movietracker import db, create_app
from movietracker.utils import get_uuid
from movietracker.models import Genre, Movie, Series

# based on "sensorhub" example database test
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on "sensorhub" example database test
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        
    yield app

    os.close(db_fd)
    os.unlink(db_fname)

def _get_movie():
    return Movie(
        title="The Avengers",
        uuid=get_uuid(),
        actors="Robert Downey Jr.",
        release_date="11-04-2012",
        score=8.0
    )

def _get_series():
    return Series(
        title = "Breaking Bad",
        uuid=get_uuid(),
        actors = "Bryan Cranston",
        release_date = "20-01-2008",
        score = 9.5,
        seasons = 5
    )

def _get_genre(name):
    return Genre(name=name)
    
def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    with app.app_context():
        # Create everything
        movie = _get_movie()
        series = _get_series()
        genre = _get_genre("Action")

        movie.genre = genre
        series.genre = genre
        db.session.add(movie)
        db.session.add(series)
        db.session.commit()
        
        # Check that everything exists
        assert Movie.query.count() == 1
        assert Series.query.count() == 1
        assert Genre.query.count() == 1
        db_movie = Movie.query.first()
        db_series = Series.query.first()
        db_genre = Genre.query.first()
        
        # Check all relationships (both sides)
        assert db_movie.genre == db_genre
        assert db_series.genre == db_genre
        assert db_movie in db_genre.movies
        assert db_series in db_genre.series

def test_foreignkey_violations(app):
    """
    Tests for foreign key violation on movie or series genre.
    """

    with app.app_context():
        # Create everything
        movie = _get_movie()
        series = _get_series()

        with pytest.raises(AttributeError):
            movie.genre = "Fantasy"
            series.genre = "Fantasy"
            db.session.add(movie)
            db.session.add(series)
            db.session.commit()

def test_modifying_models(app):
    '''
    Test that modifying movie and series attributes works correctly.
    '''

    with app.app_context():
        movie = _get_movie()
        series = _get_series()
        genre = _get_genre("Action")

        movie.genre = genre
        series.genre = genre
        db.session.add(movie)
        db.session.add(series)
        db.session.commit()

        # modify movie
        movie.title = "Avengers: Endgame"
        movie.actors="Robert Downey Jr., Chris Evans"
        movie.release_date="28-04-2018"
        movie.score=9.0

        # modify series
        series.title = "House of Cards"
        series.actors = "Bryan Cranston, Robert Downey Jr."
        series.release_date = "20-01-2010"
        series.score = 9.0
        series.seasons = 7
        
        # modify genre
        genre.name = "Comedy"

        db.session.commit()

        db_genre = Genre.query.first()
        db_movie = Movie.query.first()
        db_series = Series.query.first()
        
        # check correctness
        assert db_movie.title == "Avengers: Endgame"
        assert db_movie.actors == "Robert Downey Jr., Chris Evans"
        assert db_movie.release_date == "28-04-2018"
        assert db_movie.score == 9.0

        assert db_series.title == "House of Cards"
        assert db_series.actors == "Bryan Cranston, Robert Downey Jr."
        assert db_series.release_date == "20-01-2010"
        assert db_series.score == 9.0
        assert db_series.seasons == 7

        assert db_genre.name == "Comedy"
    
def test_modifying_item_genre(app):
    """
    Tests that genre changes correctly on movies and series and on genre
    change the item is moved to correct. Test that genre's attribute can be changed.
    """
    
    with app.app_context():
        movie = _get_movie()
        series = _get_series()
        genre1 = _get_genre("Action")
        genre2 = _get_genre("Crime")

        # give first genre
        movie.genre = genre1
        series.genre = genre1
        db.session.add(movie)
        db.session.add(series)
        db.session.commit()

        # change to second genre
        movie.genre = genre2
        series.genre = genre2
        db.session.commit()

        db_genre1 = Genre.query.filter_by(name="Action").first()
        db_genre2 = Genre.query.filter_by(name="Crime").first()
        db_movie = Movie.query.first()
        db_series = Series.query.first()
        
        # check correctness of both genres
        assert len(db_genre1.movies) == 0
        assert len(db_genre1.series) == 0
        assert len(db_genre2.movies) == 1
        assert len(db_genre2.series) == 1
        assert db_movie.genre == db_genre2
        assert db_series.genre == db_genre2
        
def test_genre_ondelete_item(app):
    """
    Tests that genre's movies or series foreign key is set to null when the movie/series is deleted.
    """
    
    with app.app_context():
        movie = _get_movie()
        series = _get_series()
        genre = _get_genre("Action")
        movie.genre = genre
        series.genre = genre

        db.session.add(movie)
        db.session.add(series)
        db.session.commit()

        db.session.delete(movie)
        db.session.delete(series)
        db.session.commit()

        # check that movies and series lists are empty
        assert len(genre.movies) == 0
        assert len(genre.series) == 0

def test_genre_ondelete_genre(app):
    """
    Tests that movies or series foreign key and genre is set to null when the genre is deleted.
    """
    
    with app.app_context():
        movie = _get_movie()
        series = _get_series()
        genre = _get_genre("Action")
        movie.genre = genre
        series.genre = genre

        db.session.add(movie)
        db.session.add(series)
        db.session.commit()
        
        db.session.delete(genre)
        db.session.commit()

        # check that movies and series lists are empty
        
        db_movie = Movie.query.first()
        db_series = Series.query.first()
        
        # check correctness of both genres
        assert Genre.query.count() == 0
        assert db_movie.genre == None
        assert db_series.genre == None
        assert db_movie.genre_id == None
        assert db_series.genre_id == None