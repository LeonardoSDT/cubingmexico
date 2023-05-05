from django.forms import ModelForm
from django import forms

from .models import CubingmexicoProfile, State, StateTeam


class CubingmexicoProfileForm(forms.ModelForm):
    class Meta:
        model = CubingmexicoProfile
        fields = ['state']

    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Selecciona una opción")


class StateTeamForm(forms.ModelForm):
    class Meta:
        model = StateTeam
        fields = ['name', 'description', 'state', 'team_logo', 'facebook_link', 'instagram_link',]

    name = forms.CharField(
        max_length=255,
        label="Nombre del Team *",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Descripción del Team",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        label="Estado del Team *",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    team_logo = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Logotipo del Team",
        required=False
    )
    facebook_link = forms.CharField(
        max_length=255,
        label="Enlace a Facebook",
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        required=False
    )
    instagram_link = forms.CharField(
        max_length=255,
        label="Enlace a Instagram",
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        required=False
    )