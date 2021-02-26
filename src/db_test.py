import os
import pytest
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

import app
from app import Movie, Series, Genre

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db
    
    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _get_movie():
    return Movie(
        title="The Avengers",
        actors="Robert Downey Jr.",
        release_date="11-04-2012",
        score=8.0
    )

def _get_series():
    return Series(
        title = "Breaking Bad",
        actors = "Bryan Cranston",
        release_date = "20-01-2008",
        score = 9.5,
        seasons = 5
    )

def _get_genre(name):
    return Genre(name=name)
    
def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    movie = _get_movie()
    series = _get_series()
    genre = _get_genre("Action")

    movie.genre = genre
    series.genre = genre
    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()
    
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

def test_foreignkey_violations(db_handle):
    """
    Tests for foreign key violation on movie or series genre.
    """

    # Create everything
    movie = _get_movie()
    series = _get_series()

    with pytest.raises(AttributeError):
        movie.genre = "Fantasy"
        series.genre = "Fantasy"
        db_handle.session.add(movie)
        db_handle.session.add(series)
        db_handle.session.commit()

def test_modifying_models(db_handle):
    '''
    Test that modifying movie and series attributes works correctly.
    '''

    movie = _get_movie()
    series = _get_series()
    genre = _get_genre("Action")

    movie.genre = genre
    series.genre = genre
    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()

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

    db_handle.session.commit()

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
    
def test_modifying_item_genre(db_handle):
    """
    Tests that genre changes correctly on movies and series and on genre
    change the item is moved to correct. Test that genre's attribute can be changed.
    """
    
    movie = _get_movie()
    series = _get_series()
    genre1 = _get_genre("Action")
    genre2 = _get_genre("Crime")

    # give first genre
    movie.genre = genre1
    series.genre = genre1
    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()

    # change to second genre
    movie.genre = genre2
    series.genre = genre2
    db_handle.session.commit()

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
        
def test_genre_ondelete_item(db_handle):
    """
    Tests that genre's movies or series foreign key is set to null when the movie/series is deleted.
    """
    
    movie = _get_movie()
    series = _get_series()
    genre = _get_genre("Action")
    movie.genre = genre
    series.genre = genre

    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()

    db_handle.session.delete(movie)
    db_handle.session.delete(series)
    db_handle.session.commit()

    # check that movies and series lists are empty
    assert len(genre.movies) == 0
    assert len(genre.series) == 0

def test_genre_ondelete_genre(db_handle):
    """
    Tests that movies or series foreign key and genre is set to null when the genre is deleted.
    """
    
    movie = _get_movie()
    series = _get_series()
    genre = _get_genre("Action")
    movie.genre = genre
    series.genre = genre

    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()
    
    db_handle.session.delete(genre)
    db_handle.session.commit()

    # check that movies and series lists are empty
    
    db_movie = Movie.query.first()
    db_series = Series.query.first()
    
    # check correctness of both genres
    assert Genre.query.count() == 0
    assert db_movie.genre == None
    assert db_series.genre == None
    assert db_movie.genre_id == None
    assert db_series.genre_id == None