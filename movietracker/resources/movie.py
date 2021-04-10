import json
import uuid
from flask_restful import Resource
from flask import Response, request, url_for
from jsonschema import validate, ValidationError
from movietracker import db
from movietracker.models import *
from movietracker.constants import *
from movietracker.utils import MovieTrackerBuilder, create_error_response

class MovieCollection(Resource):

    def get(self):
        movie = Movie.query.all()
        movie_list = []
        
        for movie in movie:
            movie_body = MovieTrackerBuilder(
                title=movie.title,
                actors=movie.actors,
                release_date=movie.release_date,
                score=movie.score,
                genre=movie.genre.name
            )
            movie_body.add_control("self", url_for("api.movieitem", movie=movie.uuid))
            movie_body.add_control("profile", MOVIE_PROFILE)
            movie_list.append(movie_body)
        
        body = MovieTrackerBuilder()
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.moviecollection"))
        body.add_control_all_genres()
        body["items"] = movie_list
        
        return Response(json.dumps(body), 200, mimetype=MASON)


class MovieItem(Resource):

    def get(self, movie):
        movie = Movie.query.filter_by(uuid=movie).first()
        if movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
            )
                
        movie_body = MovieTrackerBuilder(
            title=movie.title,
            actors=movie.actors,
            release_date=movie.release_date,
            score=movie.score,
            genre=movie.genre.name
        )
        movie_body.add_namespace("mt", LINK_RELATIONS_URL)
        movie_body.add_control("self", url_for("api.movieitem", movie=movie.uuid))
        movie_body.add_control("collection", url_for("api.moviecollection"))        
        movie_body.add_control_movies_by_genre(movie.genre.name)
        movie_body.add_control_edit(url_for("api.movieitem", movie=movie.uuid), Movie.get_schema_put())
        movie_body.add_control_delete(url_for("api.movieitem", movie=movie.uuid))
            
        return Response(json.dumps(movie_body), 200, mimetype=MASON)
        
    def put(self, movie):
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        try:
            validate(request.json, Movie.get_schema_put())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
            
        movie = Movie.query.filter_by(uuid=movie).first()
        if movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
                )

        if "genre" in request.json:
            genre = request.json["genre"]
            db_genre = Genre.query.filter_by(name=genre).first()
            if db_genre is None:
                return create_error_response(400,
                    "Invalid JSON document",
                    "Genre with name '{}' cannot be found".format(genre)
                    )
            else:
                request.json["genre"] = db_genre

        # set everything else for the new movie entry
        for i in request.json:
            setattr(movie, i, request.json[i])
            

        db.session.add(movie)
        db.session.commit()
        return Response(status=204, headers={
            "Location": url_for("api.movieitem", movie=movie.uuid)
            }, mimetype=MASON
            )
        
    def delete(self, movie):
        movie = Movie.query.filter_by(uuid=movie).first()
        if movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
                )
        
        db.session.delete(movie)
        db.session.commit()
        return Response(status=204, mimetype=MASON)
        