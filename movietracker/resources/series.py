import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from movietracker import db
from movietracker.models import *
from movietracker.constants import *
from movietracker.utils import MovieTrackerBuilder, create_error_response

class SeriesCollection(Resource):
    
    def get(self):
        body = MovieTrackerBuilder()
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.seriescollection"))
        body.add_control_all_genres()
        body["items"] = []

        for db_series in Series.query.all():
            item = MovieTrackerBuilder(
                title=db_series.title,
                actors=db_series.actors,
                release_date=db_series.release_date,
                score=db_series.score,
                seasons=db_series.seasons,
                genre=db_series.genre.name
            )
            item.add_control("self", url_for("api.seriesitem", series=db_series.uuid))
            item.add_control("profile", SERIES_PROFILE)
            body["items"].append(item)
        
        return Response(json.dumps(body), 200, mimetype=MASON)

class SeriesItem(Resource):
    
    def get(self, series):
        db_series = Series.query.filter_by(uuid=series).first()
        if db_series is None:
            return create_error_response(
                404,
                "Series not found",
                "Series with uuid '{}' does not exist".format(series)
            )
        
        body = MovieTrackerBuilder(
            title=db_series.title,
            actors=db_series.actors,
            release_date=db_series.release_date,
            score=db_series.score,
            seasons=db_series.seasons,
            genre = db_series.genre.name
        )
        body.add_namespace("mt", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.seriesitem", series=db_series.uuid))
        body.add_control("collection", url_for("api.seriesbygenrecollection", genre=db_series.genre.name))
        body.add_control_series_by_genre(db_series.genre.name)
        body.add_control_edit(url_for("api.seriesitem", series=db_series.uuid), Series.get_schema_put())
        body.add_control_delete(url_for("api.seriesitem", series=db_series.uuid))

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, series):
        db_series = Series.query.filter_by(uuid=series).first()
        if db_series is None:
            return create_error_response(
                404,
                "Series not found",
                "Series with uuid '{}' does not exist".format(series)
            )
        
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Series.get_schema_put())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

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

        for attr in request.json:
            setattr(db_series, attr, request.json[attr])
        
        db.session.add(db_series)
        db.session.commit()
        return Response(status=204, headers={
            "Location": url_for("api.seriesitem", series=db_series.uuid)
            }, mimetype=MASON
            )

    def delete(self, series):
        db_series = Series.query.filter_by(uuid=series).first()
        if db_series is None:
            return create_error_response(
                404,
                "Series not found",
                "Series with uuid '{}' does not exist".format(series)
            )
        
        db.session.delete(db_series)
        db.session.commit()
        return Response(status=204, mimetype=MASON)
