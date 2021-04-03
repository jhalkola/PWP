import json
import shortuuid
from flask import Response, request, url_for
from movietracker.constants import *


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class MovieTrackerBuilder(MasonBuilder):

    def add_control_all_movies(self):
        self.add_control(
            "mt:all-movies",
            url_for("api.moviecollection"),
            method="GET",
            title="Collection of all movies"
        )

    def add_control_all_series(self):
        self.add_control(
            "mt:all-series",
            url_for("api.seriescollection"),
            method="GET",
            title="Collection of all series"
        )

    def add_control_movies_by_genre(self, genre):
        self.add_control(
            "mt:movies-by-genre",
            url_for("api.moviesbygenrecollection", genre=genre),
            method="GET",
            title="Collection of all movies in the genre"
        )
    
    def add_control_series_by_genre(self, genre):
        self.add_control(
            "mt:series-by-genre",
            url_for("api.seriesbygenrecollection", genre=genre),
            method="GET",
            title="Collection of all series in the genre"
        )


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    return Response(json.dumps(body), status_code, mimetype=MASON)


def get_uuid():
    return shortuuid.uuid()