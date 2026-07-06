from django import forms
from .models import CollegeSuggestion


class SuggestionForm(forms.Form):
    category = forms.ChoiceField(
        choices=CollegeSuggestion.Category.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Describe your suggestion, complaint or improvement idea...",
        }),
        max_length=2000,
    )
