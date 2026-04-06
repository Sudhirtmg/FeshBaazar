from django.contrib.auth.backends import ModelBackend
from apps.accounts.models import User


class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 🔥 Instead of username → use phone
            user = User.objects.get(phone=username)

            # Check password
            if user.check_password(password):
                return user

        except User.DoesNotExist:
            return None