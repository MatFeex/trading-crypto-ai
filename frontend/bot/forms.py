from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserFormCustom(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','email']
        exclude = ['password1','password2']