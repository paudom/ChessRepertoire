from django.db.models import fields
from django import forms
from .models import Opening, Variation

# -- Opening Forms -- #
class OpeningForm(forms.ModelForm):
    class Meta:
        model = Opening
        fields = '__all__'
        exclude = ['image']

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Opening Name'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Opening Description'
                }
            ),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }
        