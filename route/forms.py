from .models import Review
from django.forms import ModelForm, TextInput, NumberInput, Textarea


# the form is related to the model
class AddReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['route_id', 'route_review', 'route_rate']

        widgets = {
            'route_id': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter route id'}),
            'route_review': Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter review'}),
            'route_rate': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter rate'})
        }
