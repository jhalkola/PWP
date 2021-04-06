import json
import re
from flask_restful import Resource
from flask import Response, request, url_for
from jsonschema import validate, ValidationError
from movietracker import db
from movietracker.models import Movie
from movietracker.constants import *
from movietracker.utils import get_uuid, MovieTrackerBuilder, create_error_response

class MovieCollection(Resource):

    def get(self):
        movies = Movie.query.all()
        movie_list = []
        
        for movie in movies:
            movie_body = MovieTrackerBuilder(
                title=movie.title,
                uuid=movie.uuid,
                actors=movie.actors,
                release_date=movie.release_date,
                score=movie.score
            )
            movie_body.add_control("self", url_for("api.movieitem", movie=movie.uuid))
            movie_body.add_control("profile", MOVIE_PROFILE)
            movie_list.append(movie_body)
        
        body = MovieTrackerBuilder(items=movie_list)
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.moviecollection"))
        body.add_control_all_genres()
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    """def post(self):
        if request.json == None:
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")
        try:
            validate(request.json, Movie.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
            
        try:
            actors = request.json["actors"]
        except KeyError:
            actors = None
            
        try:
            release_date = request.json["release_date"]
        except KeyError:
            release_date = None
            
        try:
            score = request.json["score"]
        except KeyError:
            score = None
            
        movie = Movie(title=title, uuid=get_uuid(), actors=actors, release_date=release_date, score=score)
        db.session.add(movie)
        db.session.commit()
        return Response("Storage item successully added", 201, headers={"Location": url_for("api.movieitem", uuid=movie.uuid)})"""
    
class MovieItem(Resource):

    def get(self, movie):
        # Checking if the <movie> is a title or a uuid.
        if len(movie) == 22 and re.match(r"[a-zA-Z0-9]*", movie):
            movies = Movie.query.filter_by(uuid=movie).first()
        else:
            movies = Movie.query.filter_by(title=movie).all()
            
        if movies is None:
            return create_error_response(404, "Not found", "Movie with name '{}' cannot be found.".format(title))
        
        if type(movies) is not list:
            movies = [movies]
        
        movie_list = []
        for movie in movies:
            movie_body = MovieTrackerBuilder(
                title=movie.title,
                uuid=movie.uuid,
                actors=movie.actors,
                release_date=movie.release_date,
                score=movie.score
            )
            movie_body.add_namespace("mt", LINK_RELATIONS_URL)
            movie_body.add_control("self", url_for("api.movieitem", movie=movie.uuid))
            movie_body.add_control("profile", MOVIE_PROFILE)
            movie_body.add_control("collection", url_for("api.moviecollection"))
            movie_body.add_control_movies_by_genre(movie.genre.name)
            movie_body.add_control_edit(url_for("api.movieitem", movie=movie.uuid), Movie.get_schema())
            movie_body.add_control_delete(url_for("api.movieitem", movie=movie.uuid))
            movie_list.append(movie_body)
            
        body = MovieTrackerBuilder(items=movie_list)   
        return Response(json.dumps(body), 200, mimetype=MASON)
        
    def put(self, uuid):
        if request.json == None:
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")
        try:
            validate(request.json, Movie.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
            
        movie = Movie.query.filter_by(uuid=uuid).first()
        try:
            movie.title = request.json["title"]
        except KeyError:
            pass
            
        try:
            movie.actors = request.json["actors"]
        except KeyError:
            pass
            
        try:
            movie.release_date = request.json["release_date"]
        except KeyError:
            pass
            
        try:
            movie.score = request.json["score"]
        except KeyError:
            pass

        db.session.add(movie)
        db.session.commit()
        return Response("Movie successully edited", 204, headers={"Location": url_for("api.movieitem", movie=uuid)})
        
    def delete(self, uuid):
        movie = Movie.query.filter_by(uuid=uuid).first()
        if movie is None:
            return create_error_response(404, "Not found", "Movie with name '{}' cannot be found.".format(uuid))
        
        db.session.delete(movie)
        db.session.commit()
        return Response("Movie was deleted successully", 204)