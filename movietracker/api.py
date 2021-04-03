from flask import Blueprint
from flask_restful import Api
from movietracker.resources.genre import GenreCollection, GenreItem, MoviesByGenreCollection, SeriesByGenreCollection
from movietracker.resources.movie import MovieCollection, MovieItem
from movietracker.resources.series import SeriesCollection, SeriesItem

api_bp = Blueprint("api", __name__, url_prefix="/api/")
api = Api(api_bp)

api.add_resource(GenreCollection, "/genres/")
api.add_resource(GenreItem, "/genres/<genre>/")
api.add_resource(MoviesByGenreCollection, "/genres/<genre>/movies/")
api.add_resource(SeriesByGenreCollection, "/genres/<genre>/series/")
api.add_resource(MovieCollection, "/movies/")
api.add_resource(MovieItem,
    "/movies/<movie>/",
    "/genres/<genre>/movies/<movie>/"
)
api.add_resource(SeriesCollection, "/series/")
api.add_resource(SeriesItem,
    "/series/<series>/",
    "/genres/<genre>/series/<series>/"
)