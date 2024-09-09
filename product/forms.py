# # from django import forms
# # from django.contrib.auth.models import User

# # class UserUpdateForm(forms.ModelForm):
# #     class Meta:
# #         model = User
# #         fields = ['username', 'first_name', 'last_name', 'email']

# # from django import forms
# # from .models import IngredientReview

# # class IngredientReviewForm(forms.ModelForm):
# #     class Meta:
# #         model = IngredientReview
# #         fields = ['rating', 'review_text']


# from django import forms
from django.contrib.auth.models import User
# from .models import IngredientReview

# class IngredientReviewForm(forms.ModelForm):
#     class Meta:
#         model = IngredientReview
#         fields = ['rating', 'review_text']

# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email']

# from .models import ProductRating
# # forms.py
# from django import forms
# from .models import Review

# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['product', 'review_text']  # Specify the fields to include in the form

#     # Optionally add custom validation here

# forms.py
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
