from django import forms
from .models import User, Assistent, Apotheek


class UserCreationForm(forms.ModelForm):
    # Define role choices
    ROLE_CHOICES = [
        (User.APOTHEEK, 'Apotheek'),
        (User.ASSISTENT, 'Assistent'),
    ]

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'email', 'first_name', 'last_name', 'phone_number', 'role',
                  'profile_picture']
        labels = {
            'phone_number': 'Telefoonnummer',
            'password': 'Wachtwoord',
            'confirm_password': 'Bevestig Wachtwoord',
            'email': 'E-mail',
            'first_name': 'Voornaam',
            'last_name': 'Achternaam',
            'role': 'Rol',
            'profile_picture': 'Profielfoto',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Wachtwoord en bevestig wachtwoord komen niet overeen.")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = 'Wachtwoord'
        self.fields['confirm_password'].label = 'Bevestig Wachtwoord'
        self.fields['role'].choices = self.ROLE_CHOICES  # Set the limited choices for role


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'profile_picture', 'is_active']
        labels = {
            'phone_number': 'Telefoonnummer',
            'email': 'E-mail',
            'first_name': 'Voornaam',
            'last_name': 'Achternaam',
            'profile_picture': 'Profielfoto',
            'is_active': 'Is Actief'
        }

    def clean(self):
        cleaned_data = super().clean()


class AssistentForm(forms.ModelForm):
    class Meta:
        model = Assistent
        fields = ['assistent_btwNummer', 'assistent_btwPlichtig', 'assistent_naamBedrijf', 'assistent_straatBedrijf',
                  'assistent_huisnummerBedrijf', 'assistent_postcodeBedrijf', 'assistent_stadBedrijf', 'assistent_rekeningnummer']
        labels = {
            'assistent_btwNummer': 'BTW Nummer',
            'assistent_btwPlichtig': 'BTW Plichtig',
            'assistent_naamBedrijf': 'Naam Bedrijf',
            'assistent_straatBedrijf': 'Straat Bedrijf',
            'assistent_huisnummerBedrijf': 'Huisnummer Bedrijf',
            'assistent_postcodeBedrijf': 'Postcode Bedrijf',
            'assistent_stadBedrijf': 'Stad Bedrijf',
            'assistent_rekeningnummer': 'Rekeningnummer'
        }


class ApotheekForm(forms.ModelForm):
    class Meta:
        model = Apotheek
        fields = ['apotheek_btwNummer', 'apotheek_btwPlichtig', 'apotheek_naamBedrijf', 'apotheek_straatBedrijf',
                  'apotheek_huisnummerBedrijf', 'apotheek_postcodeBedrijf', 'apotheek_stadBedrijf'
                  ]
        labels = {
            'apotheek_btwNummer': 'BTW Nummer',
            'apotheek_btwPlichtig': 'BTW Plichtig',
            'apotheek_naamBedrijf': 'Naam Bedrijf',
            'apotheek_straatBedrijf': 'Straat Bedrijf',
            'apotheek_huisnummerBedrijf': 'Huisnummer Bedrijf',
            'apotheek_postcodeBedrijf': 'Postcode Bedrijf',
            'apotheek_stadBedrijf': 'Stad Bedrijf',
        }


class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Wachtwoord")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Bevestig Wachtwoord")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Wachtwoorden komen niet overeen")

        return cleaned_data
