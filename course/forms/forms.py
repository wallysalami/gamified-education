from django.contrib.auth.forms import PasswordResetForm
from captcha.fields import ReCaptchaField
from django.conf import settings

class CaptchaPasswordResetForm(PasswordResetForm):
	captcha = (
		ReCaptchaField() 
		if settings.RECAPTCHA_PUBLIC_KEY != '' and settings.RECAPTCHA_PRIVATE_KEY != ''
		else None
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['email'].widget.attrs.update({'autofocus': 'autofocus'})
