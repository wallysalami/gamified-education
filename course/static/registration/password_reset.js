if (document.readyState !== "loading") {
	configureForm();
} else {
	document.addEventListener(
	    'DOMContentLoaded',
	    configureForm
	)
}

function configureForm() {
	var passwordResetSubmittingWarning = document.getElementById('submitting-warning')
    var passwordResetForm = document.getElementById('password_reset_form')
    if (passwordResetSubmittingWarning != null && passwordResetForm != null) {
        passwordResetForm.addEventListener(
            'submit',
            function (event)
            {
            	event.preventDefault()
            	passwordResetForm.style.display = 'none';
				passwordResetSubmittingWarning.style.display = 'block';
            	
            	setTimeout(
            		function () {
            			passwordResetForm.submit()
            		},
            		200
            	)
            },
            false
        );
    }
}