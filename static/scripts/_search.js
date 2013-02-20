function hide_tab(index) {
    $("#results_"+index).hide();
    $("#tab_"+index).parent().removeClass("current");
}
function show_tab(index) {
    $("#results_"+index).show();
    var count = $("#results_"+index).attr('count');
    $(".controls .count").text(String(count) + ((count !== 1) ? " Results" : " Result"));
    $("#tab_"+index).parent().addClass("current");
}
function details_empty() {
    $(".details .empty").show();
    $(".details .loading").hide();
    $(".details .error").hide();
    $(".details .more").hide();
}
function details_loading() {
    $(".details .empty").show();
    $(".details .loading").show();
    $(".details .error").hide();
    $(".details .more").hide();
}
function details_error(message) {
    $(".details .empty").show();
    $(".details .loading").hide();
    $(".details .error").text(message).show();
    $(".details .more").hide();
}
function details_show(details) {
    $(".details .more .name").text(details.name);
    $(".details .more .institution").text(details.department.institution.name);
    $(".details .more .department").text(details.department.name);
    $(".details .more .contact").html(details.contact.name + " (<a href='mailto:" + details.contact.email + "'>" + details.contact.email +"</a>)");
    $(".details .more .keywords .loaded").text(details.keywords.join(", "));
    $(".details .more .details .loaded").text(details.details);
    if (details.url) {
        var a = $("<a>");
        a.attr("href",details.url);
        a.text(details.url);
        $(".details .more .url").empty().append(a).show();
    }
    else {
        $(".details .more .url").hide();
    }

    $(".details .empty").hide();
    $(".details .loading").hide();
    $(".details .error").hide();
    $(".details .more").show();
}

$(document).ready(function() {
    $("#results_1").hide();
    $(".tabs a").click(function() {
        if (!$(this).parent().hasClass("current")) {
            var index = Number($(this).attr("id").split("_")[1]);
            hide_tab((index+1) % 2);
            show_tab(index);
        }
    });
    $(".list .results tr").click(function() {
        details_loading();
        var url = "/api/" + $(this).attr("id").replace("p_", "protocol/").replace("e_", "equipment/") + "/";
        $.getJSON(url, function(data) {
            if (data.result) {
                if (data.result.equipment) {
                    details_show(data.result.equipment);
                }
                else if (data.result.protocol) {
                    details_show(data.result.protocol);
                }
            }
            else {
                details_error("There has been an error fetching the results. Please try again.");
            }
        });
    });
    
    details_empty();
});