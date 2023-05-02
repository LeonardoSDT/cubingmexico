from django.forms import ModelForm

from .models import CubingmexicoProfile


class CubingmexicoProfileForm(ModelForm):
    class Meta:
        model = CubingmexicoProfile
        fields = ['state',]