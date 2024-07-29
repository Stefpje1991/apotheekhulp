from django import forms
from .models import User, Assistent, Apotheek


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'email', 'first_name', 'last_name', 'phone_number']
        labels = {
            'phone_number': 'Telefoonnummer',
            'password': 'Wachtwoord',
            'confirm_password': 'Bevestig Wachtwoord',
            'email': 'E-mail',
            'first_name': 'Voornaam',
            'last_name': 'Achternaam',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Wachtwoord en bevestig wachtwoord komen niet overeen.")


class AssistentForm(forms.ModelForm):
    class Meta:
        model = Assistent
        fields = ['btwNummer', 'btwPlichtig', 'naamBedrijf', 'straatBedrijf',
                  'huisnummerBedrijf', 'postcodeBedrijf', 'stadBedrijf',
                  'krijgtKilometervergoeding', 'uurtarief']
        labels = {
            'btwNummer': 'BTW Nummer',
            'btwPlichtig': 'BTW Plichtig',
            'naamBedrijf': 'Naam Bedrijf',
            'straatBedrijf': 'Straat Bedrijf',
            'huisnummerBedrijf': 'Huisnummer Bedrijf',
            'postcodeBedrijf': 'Postcode Bedrijf',
            'stadBedrijf': 'Stad Bedrijf',
            'krijgtKilometervergoeding': 'Krijgt Kilometervergoeding',
            'uurtarief': 'Uurtarief',
        }


class ApotheekForm(forms.ModelForm):
    class Meta:
        model = Apotheek
        fields = ['btwNummer', 'btwPlichtig', 'naamBedrijf', 'straatBedrijf',
                  'huisnummerBedrijf', 'postcodeBedrijf', 'stadBedrijf', 'uurtarief']
        labels = {
            'btwNummer': 'BTW Nummer',
            'btwPlichtig': 'BTW Plichtig',
            'naamBedrijf': 'Naam Bedrijf',
            'straatBedrijf': 'Straat Bedrijf',
            'huisnummerBedrijf': 'Huisnummer Bedrijf',
            'postcodeBedrijf': 'Postcode Bedrijf',
            'stadBedrijf': 'Stad Bedrijf',
            'uurtarief': 'Uurtarief',
        }