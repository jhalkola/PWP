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
        // let link = "<a href='" +
        //             item["@controls"].self.href +
        //             "' onClick='followLink(event, this, renderMovie)'>show</a>";
    
        return "<tr><td>" + item.title +
                "</td><td>" + item.actors +
                "</td><td>" + item.release_date +
                "</td><td>" + item.score +
                "</td><td>" + item.genre;
                // "</td><td>" + link + "</td></tr>";
    } else {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderMovie)'>show</a>";
    
        return "<tr><td>" + item.title +
                "</td><td>" + item.actors +
                "</td><td>" + item.release_date +
                "</td><td>" + item.score +
                "</td><td>" + item.seasons +
                "</td><td>" + item.genre;
                // "</td><td>" + link + "</td></tr>";
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

// function renderSensorForm(ctrl) {
//     let form = $("<form>");
//     let name = ctrl.schema.properties.name;
//     let model = ctrl.schema.properties.model;
//     form.attr("action", ctrl.href);
//     form.attr("method", ctrl.method);
//     form.submit(submitSensor);
//     form.append("<label>" + name.description + "</label>");
//     form.append("<input type='text' name='name'>");
//     form.append("<label>" + model.description + "</label>");
//     form.append("<input type='text' name='model'>");
//     ctrl.schema.required.forEach(function (property) {
//         $("input[name='" + property + "']").attr("required", true);
//     });
//     form.append("<input type='submit' name='submit' value='Submit'>");
//     $("div.form").html(form);
// }

// function renderSensor(body) {
//     $("div.navigation").html(
//         "<a href='" +
//         body["@controls"].collection.href +
//         "' onClick='followLink(event, this, renderSensors)'>collection</a>" +
//         " | " +
//         "<a href='" +
//         body["@controls"]["senhub:measurements-first"]["href"] +
//         "' onClick='followLink(event, this, renderMeasurements)'>measurements</a>"
//     );
//     $(".resulttable thead").empty();
//     $(".resulttable tbody").empty();
//     renderSensorForm(body["@controls"].edit);
//     $("input[name='name']").val(body.name);
//     $("input[name='model']").val(body.model);
//     $("form input[type='submit']").before(
//         "<label>Location</label>" +
//         "<input type='text' name='location' value='" +
//         body.location + "' readonly>"
//     );
// }

function renderMovies(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(itemRow(item, "movie"));
    });
    // renderSensorForm(body["@controls"]["senhub:add-sensor"]);
}

function renderSeries(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Actors</th><th>Release Date</th><th>Score</th><th>Seasons</th><th>Genre</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(itemRow(item, "series"));
    });
    // renderSensorForm(body["@controls"]["senhub:add-sensor"]);
}

// function renderMeasurements(body) {
//     var controls = "";
//     if ("prev" in body["@controls"] && "next" in body["@controls"]) {
//         controls = "<a href='" +
//                 body["@controls"]["prev"]["href"] +
//                 "' onClick='followLink(event, this, renderMeasurements)'>prev</a>" +
//                 " | " +
//                 "<a href='" +
//                 body["@controls"]["next"]["href"] +
//                 "' onClick='followLink(event, this, renderMeasurements)'>next</a>";
//     }
//     else if ("prev" in body["@controls"]) {
//         controls = "<a href='" +
//                 body["@controls"]["prev"]["href"] +
//                 "' onClick='followLink(event, this, renderMeasurements)'>prev</a>";
//     }
//     else {
//         controls = "<a href='" +
//                 body["@controls"]["next"]["href"] +
//                 "' onClick='followLink(event, this, renderMeasurements)'>next</a>";
//     }
//     $("div.tablecontrols").html(
//         controls
//     );
//     $(".resulttable thead").html(
//         "<tr><th>Time</th><th>Value</th></tr>"
//     );
//     let tbody = $(".resulttable tbody");
//     tbody.empty();
//     body.items.forEach(function (item) {
//         tbody.append(
//             "<tr><td>" + item.time +
//             "</td><td>" + item.value + "</td></tr>"
//         );
//     });
// }

$(document).ready(function () {
    getResource("http://127.0.0.1:5000/api/movies/", renderMovies);
});
