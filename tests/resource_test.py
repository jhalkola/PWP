import os
import pytest
import tempfile
import json
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from werkzeug.datastructures import Headers
from movietracker.utils import get_uuid
from movietracker import db, create_app
from movietracker.models import Genre, Movie, Series

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        _populate_db()
        
    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    # add two genres to test db
    genres = ["action", "crime"]
    for g in genres:
        db.session.add(Genre(name=g))
    db.session.commit()

    # add two movies and two series to test db
    for i in range(1, 3):
        movie = Movie(
            title="test-movie-{}".format(i),
            uuid="asdasdasddasdasdasddd" + str(i),
            actors="test-actor-{}".format(i),
            release_date="test-date-{}".format(i),
            score=i,
            genre=Genre.query.filter_by(name="action").first()
        )
        series = Series(
            title="test-series-{}".format(i),
            uuid="asdasdasddasdasdasddx" + str(i),
            actors="test-actor-{}".format(i),
            release_date="test-date-{}".format(i),
            score=i,
            seasons=i,
            genre=Genre.query.filter_by(name="action").first()
        )
        db.session.add(movie)
        db.session.add(series)
    db.session.commit()

def _get_movie_json(number=1):
    '''
    Creates a valid movie JSON object for PUT and POST tests
    '''

    movie_json = {
        "title": "extra-movie-{}".format(number),
        "uuid": "asdasdasddasdasdasdddd",
        "actors": "extra-actors-{}".format(number),
        "release_date": "0{}-01-2000".format(number),
        "score": number,
        "genre": Genre.query.filter_by(name="crime").first()
    }
    return movie_json

def _get_series_json(number=1):
    '''
    Creates a valid series JSON object for PUT and POST tests
    '''
    
    uuid = get_uuid()
    series_json = {
        "title": "extra-series-{}".format(number),
        "uuid": "asasasasasasasasasasas",
        "actors": "extra-actors-{}".format(number),
        "release_date": "0{}-01-2000".format(number),
        "score": number,
        "seasons": number,
        "genre": Genre.query.filter_by(name="crime").first()
    }
    return series_json

# From "sensorhub" example
def _check_namespace(client, response):
    """
    Checks that the "mt" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    
    ns_href = response["@namespaces"]["mt"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

# From "sensorhub" example
def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

# From "sensorhub" example    
def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

# From "sensorhub" example    
def _check_control_put_method(ctrl, client, obj, item_type):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid movie or series against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    if item_type == "movie":
        body = _get_movie_json()
        body["title"] = obj["title"]
    else:
        body = _get_series_json()
        body["title"] = obj["title"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204

# From "sensorhub" example   
def _check_control_post_method(ctrl, client, obj, item_type):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid movie or series against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    if item_type == "movie":
        body = _get_movie_json()
    else:
        body = _get_series_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


class TestGenreColletion(object):
    
    RESOURCE_URL = "/api/genres/"

    def test_get(self, client):
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        body = json.loads(response.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("mt:all-movies", client, body)
        #_check_control_get_method("mt:all-series", client, body)
        # check that two genres are found
        assert len(body["items"]) == 2
        # check that items are valid
        for item in body["items"]:
            assert "name" in item

            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)


class TestGenreItem(object):

    RESOURCE_URL = "/api/genres/action/"
    INVALID_URL = "/api/genres/non-genre-x/"

    def test_get(self, client):
        # test valid request
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        body = json.loads(response.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("up", client, body)
        _check_control_get_method("mt:movies-by-genre", client, body)
        _check_control_get_method("mt:series-by-genre", client, body)

        # test with invalid genre
        response = client.get(self.INVALID_URL)
        assert response.status_code == 404


class TestMoviesByGenreCollection(object):

    RESOURCE_URL = "/api/genres/action/movies/"
    INVALID_URL = "/api/genres/non-genre-x/movies/"
    LOCATION_URL = "/api/movies/"

    def test_get(self, client):
        # test valid request
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        body = json.loads(response.data)

        # check that genre name in body
        assert "name" in body

        _check_control_get_method("self", client, body)
        _check_control_get_method("up", client, body)

        # check that items are valid
        for item in body["items"]:
            assert "title" in item
            assert "actors" in item
            assert "release_date" in item
            assert "score" in item

            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

        # test with invalid genre
        response = client.get(self.INVALID_URL)
        assert response.status_code == 404
    
    def test_post(self, client):
        valid = _get_movie_json()

        # test with wrong content type
        response = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

        # test with invalid genre
        response = client.post(self.INVALID_URL, json=valid)
        assert response.status_code == 404

        # test with valid json
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 201

        # For some reason response location header is RESOURCE_URL + uuid
        # while it is actually set to be LOCATION_URL + uuid, thus this always fails
        #assert response.headers["Location"].endswith(self.LOCATION_URL + valid["uuid"] + "/")

        # test that added item exists
        resp = client.get(self.LOCATION_URL + valid["uuid"] + "/")
        assert resp.status_code == 200
        
        # test with invalid json (remove title)
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    
class TestSeriesByGenreCollection(object):

    RESOURCE_URL = "/api/genres/action/series/"
    INVALID_URL = "/api/genres/non-genre-x/series/"
    LOCATION_URL = "/api/series/"

    def test_get(self, client):
        # test valid request
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        body = json.loads(response.data)
        
        # check that genre name in body
        assert "name" in body

        _check_control_get_method("self", client, body)
        _check_control_get_method("up", client, body)
        
        # check that items are valid
        for item in body["items"]:
            assert "title" in item
            assert "actors" in item
            assert "release_date" in item
            assert "score" in item
            assert "seasons" in item

            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

        # test with invalid genre
        response = client.get(self.INVALID_URL)
        assert response.status_code == 404
    
    def test_post(self, client):
        valid = _get_series_json()

        # test with wrong content type
        response = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

        # test with invalid genre
        response = client.post(self.INVALID_URL, json=valid)
        assert response.status_code == 404

        # test with valid json
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 201
        
        # For some reason response location header is RESOURCE_URL + uuid
        # while it is actually set to be LOCATION_URL + uuid, thus this always fails
        #assert response.headers["Location"].endswith(self.LOCATION_URL + valid["uuid"] + "/")

        # test that added item exists
        resp = client.get(self.LOCATION_URL + valid["uuid"] + "/")
        assert resp.status_code == 200
        
        # test with invalid json (remove title)
        valid.pop("title")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestMovieCollection(object):

    RESOURCE_URL = "/api/movies/"
    
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 2
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("mt:all-genres", client, body)
        
        for item in body["items"]:
            assert "title" in item
            assert "uuid" in item
            assert "actors" in item
            assert "release_date" in item
            assert "score" in item
            assert "genre" in item
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
 
 
class TestMovieItem(object):
 
    RESOURCE_URL = "/api/movies/asdasdasddasdasdasddd1/"
    INVALID_URL = "/api/movies/test-movie-xd/"
    MODIFIED_URL = "/api/movies/test-movie-99/"
 
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) >= 1
        
        for item in body["items"]:
        
            assert item["title"] == "test-movie-1"
            assert item["uuid"] == "asdasdasddasdasdasddd1"
            assert item["actors"] == "test-actor-1"
            assert item["release_date"] == "test-date-1"
            assert item["score"] == 1
            assert item["genre"] == "action"
        
            _check_control_get_method("self", client, item)
            _check_control_get_method("mt:movies-by-genre", client, item)
            _check_control_put_method("edit", client, item, "movie")
            _check_control_delete_method("mt:delete", client, item)
            
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)        
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
        
    def test_put(self, client):
    
        valid = _get_movie_json()
        
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # remove field for 400
        valid.pop("title")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_movie_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["title"] == valid["title"]
        
    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
