from django.contrib.auth.models import User
from django import forms
from .models import IngredientReview

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
class IngredientReviewForm(forms.ModelForm):
    class Meta:
        model = IngredientReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }
