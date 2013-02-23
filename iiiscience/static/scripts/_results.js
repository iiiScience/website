RESULTS = {
    init: function() {
        $("#results_1").hide();
        $(".tabs a").click(function() {
            if (!$(this).parent().hasClass("current")) {
                var index = Number($(this).attr("id").split("_")[1]);
                RESULTS.hide_tab((index+1) % 2);
                RESULTS.show_tab(index);
            }
        });
        $(".list .results tr").click(function() {
            RESULTS.details_loading();
            var url = "/api/" + $(this).attr("id").replace("p_", "protocol/").replace("e_", "equipment/") + "/";
            $.getJSON(url, function(data) {
                if (data.result) {
                    if (data.result.equipment) {
                        RESULTS.details_show(data.result.equipment);
                    }
                    else if (data.result.protocol) {
                        RESULTS.details_show(data.result.protocol);
                    }
                }
                else {
                    UTIL.error("There has been an error fetching the details. Please try again.");
                }
            });
        });
        RESULTS.details_empty();
    },
    hide_tab: function(index) {
        $("#results_"+index).hide();
        $("#tab_"+index).parent().removeClass("current");
    },
    show_tab: function(index) {
        $("#results_"+index).show();
        var count = $("#results_"+index).attr('count');
        $(".controls .count").text(String(count) + ((count !== 1) ? " Results" : " Result"));
        $("#tab_"+index).parent().addClass("current");
    },
    details_empty: function() {
        $(".details .empty").show();
        $(".details .loading").hide();
        $(".details .more").hide();
    },
    details_loading: function() {
        $(".details .empty").show();
        $(".details .loading").show();
        $(".details .more").hide();
    },
    details_show: function(details) {
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
        $(".details .more").show();
    }
}