from django import forms
from .models import LinkBetweenAssistentAndApotheek

class LinkBetweenAssistentAndApotheekForm(forms.ModelForm):
    class Meta:
        model = LinkBetweenAssistentAndApotheek
        fields = [
            'assistent',
            'apotheek',
            'uurtariefAssistent',
            'uurtariefApotheek',
            'kilometervergoeding',
            'afstandInKilometers',
            'actief'
        ]
        labels = {
            'afstandInKilometers': 'Afstand in Kilometers',
            'uurtariefAssistent': 'Uurtarief van Assistent',
            'uurtariefApotheek': 'Uurtarief aan Apotheek',
        }

    def __init__(self, *args, **kwargs):
        super(LinkBetweenAssistentAndApotheekForm, self).__init__(*args, **kwargs)

        # Customize the label for the Assistent field
        if 'assistent' in self.fields:
            self.fields['assistent'].label_from_instance = lambda obj: f"{obj.user.first_name} {obj.user.last_name}"

        # Customize the label for the Apotheek field
        if 'apotheek' in self.fields:
            self.fields['apotheek'].label_from_instance = lambda obj: f"{obj.apotheek_naamBedrijf}"
