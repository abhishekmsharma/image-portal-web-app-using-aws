$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				username : $('#usernameInput').val(),
				password: $('#passwordInput').val(),
				email : $('#emailInput').val()
			},
			type : 'POST',
			url : '/signup'
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