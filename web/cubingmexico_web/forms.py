from django.forms import ModelForm
from django import forms

from .models import CubingmexicoProfile, State


class CubingmexicoProfileForm(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Selecciona una opción")

    class Meta:
        model = CubingmexicoProfile
        fields = ['state']