const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";
const ENTRYPOINT = "http://127.0.0.1:5000/api/";

// from "sensorhub" example
function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    //let msgs = jqxhr.responseJSON["@error"]["@messages"];
    $("div.notification").html(
        "<p class='error'>" + msg + "</p>"
        //"<p class='error'>" + msgs + "</p>" 
        );
}

// from "sensorhub" example
function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

// from "sensorhub" example
function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

// from "sensorhub" example
function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function deleteData(href, postProcessor) {
    $.ajax({
        url: href,
        type: "DELETE",
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function itemRow(item, type) {
    if (type == "movie") {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderMovieItem)'>Edit</a>";
        return "<tr><td>" + item.title +
                "</td><td>" + item.actors +
                "</td><td>" + item.release_date +
                "</td><td>" + item.score +
                "</td><td>" + item.genre +
                "</td><td>" + link + "</td></tr>";
    }
    else if (type == "series") {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderSeriesItem)'>Edit</a>";
    
        return "<tr><td>" + item.title +
                "</td><td>" + item.actors +
                "</td><td>" + item.release_date +
                "</td><td>" + item.score +
                "</td><td>" + item.seasons +
                "</td><td>" + item.genre +
                "</td><td>" + link + "</td></tr>";
    }
    else {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderGenreItem)'>Edit</a>";
        return "<tr><td>" + item.name +
                "</td><td>" + link + "</td></tr>";
    }
}

function appendItemRow(body) {
    let form = $("div.form form");
    type = form.attr("type")
    $(".resulttable tbody").append(itemRow(body, type));
}

// from "sensorhub" example
function getSubmittedItem(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendItemRow);
    }
}

function getAfterDelete(data, status, jqxhr) {
    let href = $(document).attr("lastLocation")[0]
    let name = $(document).attr("lastLocation")[1]
    if (name == "movies") {
        getResource(href, renderMovies);
    }
    else if (name == "moviesbygenre") {
        getResource(href, renderMoviesByGenre);
    }
    else if (name == "series") {
        getResource(href, renderSeries);
    }
    else if (name == "seriesbygenre") {
        getResource(href, renderSeriesByGenre);
    }
}

// from "sensorhub" example
function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function submitItem(event) {
    event.preventDefault();

    let form = $("div.form form");
    let data = {};
    data.title = $("input[name='title']").val();
    data.actors = $("input[name='actors']").val();
    data.release_date = $("input[name='release_date']").val();
    data.score = parseFloat($("input[name='score']").val());
    if (form.attr("type") == "series") {
        data.seasons = parseInt($("input[name='seasons']").val());
    }
    if (form.attr("method") == "PUT") {
        data.genre = $("input[name='genre']").val();
    }
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedItem);
}

function deleteItem(event) {
    event.preventDefault();

    let form = $("div.form form");
    deleteData(form.attr("action"), getAfterDelete);
}

function renderItemForm(ctrl, type) {
    let form = $("<form>");
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.attr("type", type)
    form.submit(submitItem);
    for (attr in ctrl.schema.properties) {
        prop = ctrl.schema.properties[attr]
        form.append("<label>" + prop.description + "</label>");
        form.append("<input type='text' name=" + attr + ">");
    }
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='action' value='Save'>");
    if (ctrl.method == "PUT") {
        form.append("<input type='button' value='Delete' onClick='deleteItem(event)'>");
    }
    $("div.form").html(form);
}

function renderMovieItem(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["collection"]["href"] +
        "' onClick='followLink(event, this, renderMovies)'>All Movies</a>" +
        " | " +
        "<a href='" +
        body["@controls"]["mt:movies-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderMoviesByGenre)'>" + body.genre + " Movies</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderItemForm(body["@controls"].edit, "movie");
    for (attr in body) {
        if ((attr == "@namespaces") || (attr == "@controls")) {
            continue
        }
        $("input[name=" + attr + "]").val(body[attr]);
    }
}

function renderMovies(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-genres"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a>" +
        " | " +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        for (i in item) {
            if (item[i] === null) {
                item[i] = "";
            }
        }
        tbody.append(itemRow(item, "movie"));
    });
    $(document).attr("lastLocation", [body["@controls"].self.href, "movies"])
    
    $("div.notification").empty();
    $("div.form").empty();
}

function renderMoviesByGenre(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["up"]["href"] +
        "' onClick='followLink(event, this, renderGenreItem)'>"  + body.name + " Genre</a>" + 
        " | " +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        for (i in item) {
            if (item[i] === null) {
                item[i] = "";
            }
        }
        tbody.append(itemRow(item, "movie"));
    });
    $(document).attr("lastLocation", [body["@controls"].self.href, "moviesbygenre"])
    $("div.notification").empty();
    renderItemForm(body["@controls"]["mt:add-movie"], "movie");
}

function renderSeriesItem(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["collection"]["href"] +
        "' onClick='followLink(event, this, renderSeries)'>All Series</a>" +
        " | " +
        "<a href='" +
        body["@controls"]["mt:series-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderSeriesByGenre)'>" + body.genre + " Series</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    renderItemForm(body["@controls"].edit, "series");
    for (attr in body) {
        if ((attr == "@namespaces") || (attr == "@controls")) {
            continue
        }
        $("input[name=" + attr + "]").val(body[attr]);
    }
}

function renderSeries(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-genres"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a>" +
        " | " +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Seasons</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        for (i in item) {
            if (item[i] === null) {
                item[i] = "";
            }
        }
        tbody.append(itemRow(item, "series"));
    });
    $(document).attr("lastLocation", [body["@controls"].self.href, "series"])
    $("div.notification").empty();
    $("div.form").empty();
}

function renderSeriesByGenre(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["up"]["href"] +
        "' onClick='followLink(event, this, renderGenreItem)'>"  + body.name + " Genre</a>" +
        " | " +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Seasons</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        for (i in item) {
            if (item[i] === null) {
                item[i] = "";
            }
        }
        tbody.append(itemRow(item, "series"));
    });
    $(document).attr("lastLocation", [body["@controls"].self.href, "seriesbygenre"])
    $("div.notification").empty();
    renderItemForm(body["@controls"]["mt:add-series"], "series");
}

function renderGenreItem(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["up"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a><br>" +
        "<a href='" +
        body["@controls"]["mt:movies-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderMoviesByGenre)'>" + body.name + " Movies</a><br>" +
        "<a href='" +
        body["@controls"]["mt:series-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderSeriesByGenre)'>" + body.name + " Series</a><br>" +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("div.form").empty();
}

function renderGenres(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-movies"]["href"] +
        "' onClick='followLink(event, this, renderMovies)'>All Movies</a>" +
        " | " +
        "<a href='" +
        body["@controls"]["mt:all-series"]["href"] +
        "' onClick='followLink(event, this, renderSeries)'>All Series</a>" +
        " | " +
        "<a href='" +
        ENTRYPOINT +
        "' onClick='followLink(event, this, renderEntrypoint)'>Home Page</a>"
    );
    $("div.tablecontrols").empty();
    $("div.notification").empty();
    $(".resulttable thead").html(
        "<tr><th>Name</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        for (i in item) {
            if (item[i] === null) {
                item[i] = "";
            }
        }
        tbody.append(itemRow(item, "genre"));
    });
}

function renderEntrypoint(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-movies"]["href"] +
        "' onClick='followLink(event, this, renderMovies)'>All Movies</a><br>" +
        "<a href='" +
        body["@controls"]["mt:all-series"]["href"] +
        "' onClick='followLink(event, this, renderSeries)'>All Series</a><br>" +
        "<a href='" +
        body["@controls"]["mt:all-genres"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    $("div.notification").empty();
    $("div.form").empty();
}

$(document).ready(function () {
    getResource(ENTRYPOINT, renderEntrypoint);
});
