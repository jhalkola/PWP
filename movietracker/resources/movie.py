import json
from flask_restful import Resource
from flask import Response, request, url_for
from jsonschema import validate, ValidationError
from movietracker import db
from movietracker.models import *
from movietracker.constants import *
from movietracker.utils import MovieTrackerBuilder, create_error_response

class MovieCollection(Resource):

    def get(self):
        body = MovieTrackerBuilder()
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.moviecollection"))
        body.add_control_all_genres()
        body["items"] = []
        
        for db_movie in Movie.query.all():
            item = MovieTrackerBuilder(
                title=db_movie.title,
                actors=db_movie.actors,
                release_date=db_movie.release_date,
                score=db_movie.score,
                genre=db_movie.genre.name
            )
            item.add_control("self", url_for("api.movieitem", movie=db_movie.uuid))
            item.add_control("profile", MOVIE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class MovieItem(Resource):

    def get(self, movie):
        db_movie = Movie.query.filter_by(uuid=movie).first()
        if db_movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
            )
                
        body = MovieTrackerBuilder(
            title=db_movie.title,
            actors=db_movie.actors,
            release_date=db_movie.release_date,
            score=db_movie.score,
            genre=db_movie.genre.name
        )
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.movieitem", movie=db_movie.uuid))
        body.add_control("collection", url_for("api.moviecollection"))        
        body.add_control_movies_by_genre(db_movie.genre.name)
        body.add_control_edit(url_for("api.movieitem", movie=db_movie.uuid), Movie.get_schema_put())
        body.add_control_delete(url_for("api.movieitem", movie=db_movie.uuid))
            
        return Response(json.dumps(body), 200, mimetype=MASON)
        
    def put(self, movie):
        # check that movie exists
        db_movie = Movie.query.filter_by(uuid=movie).first()
        if db_movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
                )

        # check media type
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Request content type must be JSON")

        # validate JSON
        try:
            validate(request.json, Movie.get_schema_put())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        # check that given genre exists
        genre = request.json["genre"]
        db_genre = Genre.query.filter_by(name=genre).first()
        if db_genre is None:
            return create_error_response(400,
                "Invalid JSON document",
                "Genre with name '{}' cannot be found".format(genre)
                )
        else:
            request.json["genre"] = db_genre

        # set properties
        for attr in Movie.get_schema_put()["properties"]:
            try:
                setattr(db_movie, attr, request.json[attr])
            except KeyError:
                return create_error_response(400,
                    "Missing property in JSON file",
                    "Property '{}' was not found".format(attr)
                    )

        db.session.add(db_movie)
        db.session.commit()
        return Response(status=204, mimetype=MASON)
        
    def delete(self, movie):
        # check that movie exists
        db_movie = Movie.query.filter_by(uuid=movie).first()
        if db_movie is None:
            return create_error_response(404,
                "Movie not found",
                "Movie with uuid '{}' cannot be found".format(movie)
                )
        
        db.session.delete(db_movie)
        db.session.commit()
        return Response(status=204, mimetype=MASON)
        