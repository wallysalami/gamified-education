from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django_recaptcha.fields import ReCaptchaField
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

	def get_users(self, email):
		# removed check verifying if password is unusable
		user_model = get_user_model()
		active_users = user_model._default_manager.filter(**{
            '%s__iexact' % user_model.get_email_field_name(): email,
            'is_active': True,
        })

		return active_users

class UsernameOrEmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _("Username / Email")


class UserCreationForm(UserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")

        return password2