from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel._default_manager.get(email=username.lower())
            except UserModel.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                UserModel().set_password(password)
                return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None