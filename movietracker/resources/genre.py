import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from movietracker.models import Genre
from movietracker.constants import *
from movietracker.utils import MovieTrackerBuilder, create_error_response

class GenreCollection(Resource):
    
    def get(self):
        body = MovieTrackerBuilder()
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.genrecollection"))
        body.add_control_all_movies()
        body.add_control_all_series()
        body["items"] = []

        for db_genre in Genre.query.all():
            item = MovieTrackerBuilder(
                name=db_genre.name
            )
            item.add_control("self", url_for("api.genre", genre=db_genre.name))
            item.add_control("profile", url_for(GENRE_PROFILE))
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class GenreItem(Resource):

    def get(self, genre):
        genre = Genre.query.filter_by(name=genre).first()

        if genre is None:
            return create_error_response(404,
                "Genre not found",
                "Genre with name '{}' does not exist".format(genre)
            )

        body = MovieTrackerBuilder(
            name=genre.name
        )
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.genreitem", genre=genre.name))
        body.add_control("up", url_for("api.genrecollection"))
        body.add_control_movies_by_genre(genre.name)
        body.add_control_series_by_genre(genre.name)

        return Response(json.dumps(body), 200, mimetype=MASON)


class MoviesByGenreCollection(Resource):
    pass


class SeriesByGenreCollection(Resource):
    pass