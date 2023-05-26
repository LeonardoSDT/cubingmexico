from django.db import models

# Create your models here.

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from cubingmexico_wca.models import Person
from phonenumber_field.modelfields import PhoneNumberField

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
    three_letter_code = models.CharField(max_length=3)

    class Meta:
        verbose_name = _('Estado de la Republica Mexicana')
        verbose_name_plural = _('Estados de la Republica Mexicana')

    def __str__(self):
        return self.name

class StateTeam(models.Model):
    def __str__(self):
        return str(self.name)

    name = models.CharField(_("Nombre del team"), max_length=255)
    description =  models.TextField(_("Descripción del team"), null=True, blank=True, default='')
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name=_('Estado de la Republica Mexicana'))
    team_logo = models.ImageField(verbose_name=_("Logotipo del team"), upload_to='img/team_logos/', null=True, blank=True)
    facebook_link = models.URLField(_("Enlace de Facebook"), max_length=255, blank=True, default='')
    instagram_link = models.URLField(_("Enlace de Instagram"), max_length=255, blank=True, default='')
    phone_number = PhoneNumberField(_("Número de teléfono"), blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('edit_stateteam', 'Can edit state team'),
        )
        verbose_name = _('Team estatal')
        verbose_name_plural = _('Teams estatales')

class PersonStateTeam(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, verbose_name=_('Persona con WCAID'))
    state_team = models.ForeignKey(StateTeam, on_delete=models.CASCADE, verbose_name=_('Estado de la Republica Mexicana'))

    def __str__(self):
        return str(f'{self.person.name}, {self.state_team.name}')
    
    class Meta:
        unique_together = ('person', 'state_team')
        verbose_name = _('Miembro de team')
        verbose_name_plural = _('Miembros de team')

class CubingmexicoProfile(models.Model):
    def __str__(self):
        return str(self.user.wcaprofile.name)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, default='')
    person_state_team = models.ForeignKey(PersonStateTeam, on_delete=models.SET_NULL, null=True, blank=True, default='')
    is_state_team_leader = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Perfil de Cubingmexico')
        verbose_name_plural = _('Perfiles de Cubingmexico')
