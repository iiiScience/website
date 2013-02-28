UPLOAD = {
	init: function() {
		$('form a.button').click(function(){
			$(this).parents('form').submit();
			return false;
		});
		$('form').submit(function() {
			if (UPLOAD.validate(this)) {
				UPLOAD.make_equipment(this);
			}
			else {
				UTIL.error('There is something wrong with the details you have provided');
			}
			return false;
		});
		$("#aall").change(function() {
			if ($(this).is(':checked')) {
				$('.sa input').not(":disabled").prop('checked', true);
			}
		});
		$("#auni").change(function() {
			if ($(this).is(':checked')) {
				$('.sa.universities input').not(":disabled").prop('checked', true);
				$('.sa.companies input').not(":disabled").prop('checked', false);
			}
		});
		$("#acom").change(function() {
			if ($(this).is(':checked')) {
				$('.sa.companies input').not(":disabled").prop('checked', true);
				$('.sa.universities input').not(":disabled").prop('checked', false);
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
	},
	validate: function(form) {
		var valid = true;
		var input = [$("input[name='name']"),
					 $("textarea[name='details']"),
					 $("#depts"),
					 $("#conts"),
					 $("input[name='contactemail']")];
		$.each(input, function(index, value) {
			if (!value.val()) {
				value.parents('li').addClass("error");
				valid = false;
			}
		});
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
			$.ajax({
				type: "POST",
				url: '/api/equipment/',
				data: JSON.stringify(e),
				contentType: 'application/json',
				dataType: "json",
				success: function(data, textStatus, jqXHR) {
					if (data.error) {
						UTIL.error('There was an error with your submission, something went wrong on our end. Sorry, please try again later.');
					}
					else {
						window.location = "/upload/thankyou/";
					}
				}
			});
		});
	}
}