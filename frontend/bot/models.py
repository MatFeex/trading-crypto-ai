from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=200, null=True)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    cash = models.FloatField(default=0)
    active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Trade(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    side = models.CharField(max_length=4)
    price = models.FloatField()
    quantity = models.FloatField()
    amount = models.FloatField()
    profit = models.FloatField()
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField()

    class Meta :
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)
