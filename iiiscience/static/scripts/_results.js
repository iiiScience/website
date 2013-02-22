RESULTS = {
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
        $(".details .error").hide();
        $(".details .more").hide();
    },
    details_loading: function() {
        $(".details .empty").show();
        $(".details .loading").show();
        $(".details .error").hide();
        $(".details .more").hide();
    },
    details_error: function(message) {
        $(".details .empty").show();
        $(".details .loading").hide();
        $(".details .error").text(message).show();
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
        $(".details .error").hide();
        $(".details .more").show();
    }
}