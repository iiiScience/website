// http://viget.com/inspire/extending-paul-irishs-comprehensive-dom-ready-execution
IIISCIENCE = {
	common: function() {

	},
	results: RESULTS.init,
	upload: UPLOAD.init
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
  	error: function(message, persistent) {
  		var delay = (persistent) ? 0 : 5000;
		alertify.error(message, delay);
	},
	warn: function(message, persistent) {
		var delay = (persistent) ? 0 : 5000;
		alertify.warn(message, delay);
	},
	info: function(message, persistent) {
		var delay = (persistent) ? 0 : 5000;
		alertify.log(message, "", delay);
	},
	success: function(message, persistent) {
		var delay = (persistent) ? 0 : 5000;
		alertify.success(message, delay);
	}
};
$(document).ready(UTIL.loadEvents);