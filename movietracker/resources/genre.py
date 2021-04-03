import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.ext.declarative.api import AbstractConcreteBase
from movietracker.models import Genre, Series
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
            item.add_control("self", url_for("api.genreitem", genre=db_genre.name))
            item.add_control("profile", GENRE_PROFILE)
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
        body.add_control("self", url_for("api.moviesbygenrecollection", genre=genre.name))
        body.add_control("up", url_for("api.genreitem", genre=genre.name))
        body["items"] = []
        
        for db_movie in genre.movies:
            item = MovieTrackerBuilder(
                title=db_movie.title,
                actors=db_movie.actors,
                release_date=db_movie.release_date,
                score=db_movie.score
            )
            item.add_control("self", url_for("api.movieitem", genre=genre.name, movie=db_movie.uuid))
            item.add_control("profile", MOVIE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class SeriesByGenreCollection(Resource):

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
        body.add_control("self", url_for("api.seriesbygenrecollection", genre=genre.name))
        body.add_control("up", url_for("api.genreitem", genre=genre.name))
        body["items"] = []
        
        for db_series in genre.series:
            item = MovieTrackerBuilder(
                title=db_series.title,
                actors=db_series.actors,
                release_date=db_series.release_date,
                score=db_series.score
            )
            item.add_control("self", url_for("api.seriesitem", genre=genre.name, series=db_series.uuid))
            item.add_control("profile", SERIES_PROFILE)
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)