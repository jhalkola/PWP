import os
import pytest
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

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

def _get_genre():
    return Genre(name="Action")

    
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
    genre = _get_genre()

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
    
# def test_location_sensor_one_to_one(db_handle):
#     """
#     Tests that the relationship between sensor and location is one-to-one.
#     i.e. that we cannot assign the same location for two sensors.
#     """
    
#     location = _get_location()
#     sensor_1 = _get_sensor(1)
#     sensor_2 = _get_sensor(2)
#     sensor_1.location = location
#     sensor_2.location = location
#     db_handle.session.add(location)
#     db_handle.session.add(sensor_1)
#     db_handle.session.add(sensor_2)    
#     with pytest.raises(IntegrityError):
#         db_handle.session.commit()
        
def test_genre_ondelete_item(db_handle):
    """
    Tests that measurement's sensor foreign key is set to null when the sensor
    is deleted.
    """
    
    movie = _get_movie()
    series = _get_series()
    genre = _get_genre()
    movie.genre = genre
    series.genre = genre
    db_handle.session.add(movie)
    db_handle.session.add(series)
    db_handle.session.commit()
    db_handle.session.delete(movie)
    db_handle.session.delete(series)
    db_handle.session.commit()
    assert genre.movies is None
    assert genre.series is None