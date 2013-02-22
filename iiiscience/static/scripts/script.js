// http://viget.com/inspire/extending-paul-irishs-comprehensive-dom-ready-execution
IIISCIENCE = {
	common: function() {

	},
	results: function() {
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
		            RESULTS.details_error("There has been an error fetching the results. Please try again.");
		        }
		    });
		});
		RESULTS.details_empty();
	}
};
UTIL = {
  	fire: function(func, args) {
    	var namespace = IIISCIENCE;
    	if (typeof namespace[func] == 'function'){
      		namespace[func](args);
    	}
  	},
	loadEvents : function() {
    	UTIL.fire('common');
    	$.each(document.body.className.split(/\s+/), function(i,classnm) {
      		UTIL.fire(classnm);
    	});
  	}
};
$(document).ready(UTIL.loadEvents);