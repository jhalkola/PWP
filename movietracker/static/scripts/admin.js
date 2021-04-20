const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

// function sendData(href, method, item, postProcessor) {
//     $.ajax({
//         url: href,
//         type: method,
//         data: JSON.stringify(item),
//         contentType: PLAINJSON,
//         processData: false,
//         success: postProcessor,
//         error: renderError
//     });
// }

function itemRow(item, type) {
    if (type == "movie") {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderMovieItem)'>show</a>";
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
                    "' onClick='followLink(event, this, renderSeriesItem)'>show</a>";
    
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
                    "' onClick='followLink(event, this, renderGenreItem)'>show</a>";
        let name = item.name.charAt(0).toUpperCase() + item.name.slice(1)
        return "<tr><td>" + name +
                "</td><td>" + link + "</td></tr>";
    }
}

function appendItemRow(body, type) {
    $(".resulttable tbody").append(itemRow(body, type));
}

// function getSubmittedSensor(data, status, jqxhr) {
//     renderMsg("Successful");
//     let href = jqxhr.getResponseHeader("Location");
//     if (href) {
//         getResource(href, appendSensorRow);
//     }
// }

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

// function submitSensor(event) {
//     event.preventDefault();

//     let data = {};
//     let form = $("div.form form");
//     data.name = $("input[name='name']").val();
//     data.model = $("input[name='model']").val();
//     sendData(form.attr("action"), form.attr("method"), data, getSubmittedSensor);
// }

function renderItemForm(ctrl) {
    let form = $("<form>");
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    //form.submit(submitSensor);
    for (attr in ctrl.schema.properties) {
        prop = ctrl.schema.properties[attr]
        form.append("<label>" + prop.description + "</label>");
        form.append("<input type='text' name=" + attr + ">");
    }
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    //form.append("<input type='submit' name='submit' value='Submit'>");
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
        "' onClick='followLink(event, this, renderMoviesByGenre)'>Movies by Genre</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderItemForm(body["@controls"].edit);
    for (attr in body) {
        $("input[name=" + attr + "]").val(body[attr]);
    }
    // $("form input[type='submit']").before(
    //     "<label>Location</label>" +
    //     "<input type='text' name='location' value='" +
    //     body.location + "' readonly>"
    // );
}

function renderSeriesItem(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["collection"]["href"] +
        "' onClick='followLink(event, this, renderSeries)'>All Series</a>" +
        " | " +
        "<a href='" +
        body["@controls"]["mt:series-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderSeriesByGenre)'>Series by Genre</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderItemForm(body["@controls"].edit);
    for (attr in body) {
        $("input[name=" + attr + "]").val(body[attr]);
    }
}

function renderGenreItem(body) {
    let name = body.name.charAt(0).toUpperCase() + body.name.slice(1)
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["up"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a><br>" +
        "<a href='" +
        body["@controls"]["mt:movies-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderMoviesByGenre)'>" + name + " Movies</a><br>" +
        "<a href='" +
        body["@controls"]["mt:series-by-genre"]["href"] +
        "' onClick='followLink(event, this, renderSeriesByGenre)'>" + name + " Series</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
}

function renderMovies(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-genres"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(itemRow(item, "movie"));
    });
    $("div.form").empty();
}

function renderSeries(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["mt:all-genres"]["href"] +
        "' onClick='followLink(event, this, renderGenres)'>All Genres</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Seasons</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(itemRow(item, "series"));
    });
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
        "' onClick='followLink(event, this, renderSeries)'>All Series</a>"
    );
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Name</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
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
}

$(document).ready(function () {
    getResource("http://127.0.0.1:5000/api/", renderEntrypoint);
});
