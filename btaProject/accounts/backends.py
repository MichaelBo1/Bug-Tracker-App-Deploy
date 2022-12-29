from django.contrib.auth import get_user_model


class DemoUserAuthenticationBackend:
    """Authenticates one of 4 demo users to login with"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            if user.is_demo:
                return user
        except UserModel.DoesNotExist:
            return None
        
        
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None