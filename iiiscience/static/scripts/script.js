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
	},
	upload: function() {
		$('form a.button').click(function(){
			$(this).parents('form').submit();
			return false;
		});
		$('form').submit(function() {
			if (UPLOAD.validate(this)) {
				UPLOAD.make_equipment(this);
			}
			return false;
		});
		$("#aall").change(function() {
			if ($(this).is(':checked')) {
				$('.sa input').prop('checked', true);
			}
		});
		$("#auni").change(function() {
			if ($(this).is(':checked')) {
				$('.sa.universities input').prop('checked', true);
				$('.sa.companies input').prop('checked', false);
			}
		});
		$("#acom").change(function() {
			if ($(this).is(':checked')) {
				$('.sa.companies input').prop('checked', true);
				$('.sa.universities input').prop('checked', false);
			}
		});
		$(".sa.universities input").change(function() {
			if ($(this).is(':checked')) {
				if (!$('.sa.universities input').not(':checked').length) {
					if ($("#acom").is(':checked')) {
						$("#aall").prop('checked', true);
					}
					else {
						$("#auni").prop('checked', true);
					}
				}
			}
			else {
				if ($("#aall").is(':checked')) {
					$("#acom").prop('checked', true);
				}
				else if ($("#auni").is(':checked')) {
					$("#auni").prop('checked', false, true);
				}
			}
		});
		$(".sa.companies input").change(function() {
			if ($(this).is(':checked')) {
				if (!$('.sa.companies input').not(':checked').length) {
					if ($("#auni").is(':checked')) {
						$("#aall").prop('checked', true);
					}
					else {
						$("#acom").prop('checked', true);
					}
				}
			}
			else {
				if ($("#aall").is(':checked')) {
					$("#auni").prop('checked', true);
				}
				else if ($("#acom").is(':checked')) {
					$("#acom").prop('checked', false, true);
				}
			}
		});	
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
  	},
  	error: function(element, message) {
		window.alert(message);
	}
};
$(document).ready(UTIL.loadEvents);