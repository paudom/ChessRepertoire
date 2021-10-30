from django import forms
from .models import Opening, Variation

# -- Opening Forms -- #
class OpeningForm(forms.ModelForm):
    class Meta:
        model = Opening
        fields = '__all__'

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
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

# -- Variation Form -- #
class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'
        exclude = ['opening', 'pgn_file']
        
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Variation Name'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Variation Description'
                }
            ),
            'on_turn': forms.NumberInput(attrs={'class': 'form-control'}),
            'nature': forms.Select(attrs={'class': 'form-control'}),
            'image_file': forms.FileInput(attrs={'class': 'form-control'})
        }
        