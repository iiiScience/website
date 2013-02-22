UPLOAD = {
	validate: function(form) {
		var valid = true;
		if (!$("input[name='name']").val()) {
			UTIL.error(this, "You must provide a name");
			valid = false;
		}
		if (!$("textarea[name='details']").val()) {
			UTIL.error(this, "You must provide some details");
			valid = false;
		}
		if (!$("#depts").val()) {
			UTIL.error(this, "You must specify a department");
			valid = false;
		}
		if (!$("#conts").val()) {
			UTIL.error(this, "You must provide a contact");
			valid = false;
		}
		if (!$("input[name='contactemail']").val()) {
			UTIL.error(this, "You must provide a contact email address");
			valid = false;
		}
		return valid;
	},
	make_department: function(name, institution, entity) {
		return $.ajax({
			type: "POST",
			url: '/api/department/',
			data: JSON.stringify({name: name, institution: Number(institution)}),
			contentType: 'application/json',
			dataType: "json",
			success: function(data, textStatus, jqXHR) {
				if (data.error) {
					entity.invalid = true;
				}
				else {
					entity.department = Number(data.success.replace('/api/department/', '').replace('/',''));
				}
			}
		});
	},
	make_contact: function(name, email, entity) {
		return $.ajax({
			type: "POST",
			url: '/api/contact/',
			data: JSON.stringify({name: name, email: email}),
			contentType: 'application/json',
			dataType: "json",
			success: function(data, textStatus, jqXHR) {
				if (data.error) {
					entity.invalid = true;
				}
				else {
					entity.contact = Number(data.success.replace('/api/contact/', '').replace('/',''));
				}
			}
		});
	},
	make_equipment: function(form) {
		var waitingOn = [];
		var e = {};
		$(form).find("input[name='name']").each(function() {
			e.name = $(this).val();
		});
		$(form).find("textarea[name='details']").each(function() {
			e.details = $(this).val();
		});
		$(form).find("input[name='department']").not(':hidden').each(function() {
			var id = $(this).next('input').val();
			if (id) {
				e.department = id;
			}
			else {
				waitingOn.push(UPLOAD.make_department($(this).val(), $("input[name='institution']").val(), e));
			}
		});
		$(form).find("input[name='contactname']").each(function() {
			waitingOn.push(UPLOAD.make_contact($(this).val(), $("input[name='contactemail']").val(), e));
		});
		e.keywords = $("#keywords").val().split(',');
		$.map(e.keywords, function(element, index) {
			e.keywords[index] = $.trim(element);
			if (!e.keywords[index]) {e.keywords.splice(index, 1);}
		});
		$.when.apply(null, waitingOn).done(function() {
			console.log(e);
			$.ajax({
				type: "POST",
				url: '/api/equipment/',
				data: JSON.stringify(e),
				contentType: 'application/json',
				dataType: "json",
				success: function(data, textStatus, jqXHR) {
					if (data.error) {
						UTIL.error(null, 'There was an error with your submission, please try again later.');
					}
					else {
						window.location = "/thankyou/";
					}
				}
			});
		});
	}
}