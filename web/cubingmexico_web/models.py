from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

from cubingmexico_wca.models import Person

class User(AbstractUser):
    has_default_password = models.BooleanField(default=True)

    def __str__(self):
        return self.username


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

class StateTeam(models.Model):
    def __str__(self):
        return str(self.name)

    name = models.CharField(max_length=255)
    description =  models.TextField(null=True, blank=True, default='')
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    team_logo = models.ImageField(upload_to='img/team_logos/', null=True, blank=True)
    facebook_link = models.URLField(max_length=255, blank=True, default='')
    instagram_link = models.URLField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('edit_stateteam', 'Can edit state team'),
        )

class PersonStateTeam(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    state_team = models.ForeignKey(StateTeam, on_delete=models.CASCADE)

    def __str__(self):
        return str(f'{self.person.name}, {self.state_team.name}')
    
    class Meta:
        unique_together = ('person', 'state_team')

class CubingmexicoProfile(models.Model):
    def __str__(self):
        return str(self.user.wcaprofile.name)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, default='')
    person_state_team = models.ForeignKey(PersonStateTeam, on_delete=models.SET_NULL, null=True, blank=True, default='')
    is_state_team_leader = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

