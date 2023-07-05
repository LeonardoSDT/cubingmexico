from django.forms import ModelForm
from django import forms

from .models import CubingmexicoProfile, State, StateTeam, PersonStateTeam
from cubingmexico_wca.models import Person
from phonenumber_field.formfields import PhoneNumberField


class CubingmexicoProfileForm(forms.ModelForm):
    class Meta:
        model = CubingmexicoProfile
        fields = ['state']

    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        empty_label="Selecciona una opción",
        widget=forms.Select(attrs={'class': 'form-control'})
        )

class StateTeamForm(forms.ModelForm):
    class Meta:
        model = StateTeam
        fields = ['name', 'description', 'team_logo', 'facebook_link', 'instagram_link', 'phone_number', 'email']

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
    phone_number = PhoneNumberField(
        label="Número de teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    email = forms.EmailField(
        max_length=255,
        label="Dirección de correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False
    )


class PersonStateTeamForm(forms.ModelForm):
    class Meta:
        model = PersonStateTeam
        fields = ['person']

    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        empty_label="Selecciona una persona",
        label="Persona",
        widget=forms.Select(attrs={'class': 'form-control'})
        )
