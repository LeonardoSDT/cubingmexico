from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    has_default_password = models.BooleanField(default=True)


class WCAProfile(models.Model):
    def __str__(self):
        return self.wca_id or self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wca_pk = models.IntegerField()
    wca_id = models.CharField(max_length=30, null=True, blank=True, unique=True)
    name = models.CharField(max_length=70)
    gender = models.CharField(max_length=10)
    country_iso2 = models.CharField(max_length=10)
    delegate_status = models.CharField(max_length=30, null=True, blank=True)
    avatar_url = models.CharField(max_length=255)
    avatar_thumb_url = models.CharField(max_length=255)
    is_default_avatar = models.BooleanField()
    wca_created_at = models.CharField(max_length=500)
    wca_updated_at = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class State(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CubingmexicoProfile(models.Model):
    def __str__(self):
        return str(self.user)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
