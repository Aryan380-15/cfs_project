from django import forms


class FeedbackReviewForm(forms.Form):
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Optional: share honest, constructive feedback (no names, no abusive language)...",
        }),
        max_length=1000,
    )
