$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				username : $('#usernameInput').val(),
				code: $('#codeInput').val()
			},
			type : 'POST',
			url : '/confirmUser'
		})
		.done(function(data) {

			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.success).show();
				$('#errorAlert').hide();
			}

		});

		event.preventDefault();

	});

});