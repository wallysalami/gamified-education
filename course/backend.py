from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                return None
        
        if user.check_password(password):
            return user

        return None